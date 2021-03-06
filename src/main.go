package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/globalsign/mgo/bson"
	"github.com/globalsign/mgo"
	"github.com/gorilla/mux"
)


var firmsColl = "firms"

type firm struct {
	ID      bson.ObjectId `json:"id" bson:"_id,omitempty"`
	Name    string        `json:"name"`
	Age     uint8         `json:"age"`
}

type firmHandler struct {
	db *mgo.Database
}

func newHandler(db *mgo.Database) *firmHandler {
	return &firmHandler{
		db: db,
	}
}

func (handler *firmHandler) post(responseWriter http.ResponseWriter, request *http.Request) {
	firm := new(firm)
	json.NewDecoder(request.Body).Decode(&firm)

	firm.ID = bson.NewObjectId()
	handler.db.C(firmsColl).Insert(firm)
	log.Printf("Created: %v", firm)

	responseWriter.WriteHeader(http.StatusOK)
	fmt.Fprintf(responseWriter, "%v", firm.ID.Hex())
}

func (handler *firmHandler) list(responseWriter http.ResponseWriter, request *http.Request) {
	firms := []firm{}
	handler.db.C(firmsColl).Find(bson.M{}).All(&firms)

	if len(firms) == 0 {
		log.Printf("No users found!")
		responseWriter.WriteHeader(http.StatusNotFound)
	} else {
		log.Printf("Found %v users!", len(firms))
		responseWriter.WriteHeader(http.StatusFound)
	}

	responseWriter.Header().Set("Content-Type", "application/json")
	json.NewEncoder(responseWriter).Encode(firms)
}

func (handler *firmHandler) get(responseWriter http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)
	id := bson.ObjectIdHex(vars["firm_id"])

	firm := new(firm)
	log.Printf("Searching for user %v...", id.Hex())

	count, _ := handler.db.C(firmsColl).Find(bson.M{"_id": id}).Count()
	if count < 1 {
		log.Printf("Not Found: %v", id.Hex())
		responseWriter.WriteHeader(http.StatusNotFound)
	} else {
		log.Printf("Found: %v", id.Hex())
		responseWriter.WriteHeader(http.StatusFound)
		handler.db.C(firmsColl).Find(bson.M{"_id": id}).One(&firm)
	}

	responseWriter.Header().Set("Content-Type", "application/json")
	json.NewEncoder(responseWriter).Encode(firm)
}

func (handler *firmHandler) delete(responseWriter http.ResponseWriter, request *http.Request) {
	vars := mux.Vars(request)
	id := bson.ObjectIdHex(vars["firm_id"])

	log.Printf("Removing user(s) with id: %v...", id.Hex())
	handler.db.C(firmsColl).Remove(bson.M{"_id": id})
	log.Printf("Removed!")

	responseWriter.WriteHeader(http.StatusOK)
	fmt.Fprintf(responseWriter, "Success!")
}

func (handler *firmHandler) deleteAll(responseWriter http.ResponseWriter, request *http.Request) {
	log.Printf("Removing all users...")
	handler.db.C(firmsColl).RemoveAll(bson.M{})
	log.Printf("Removed all users!")

	responseWriter.WriteHeader(http.StatusOK)
	fmt.Fprintf(responseWriter, "Success!")
}

func defaultHandler(responseWriter http.ResponseWriter, request *http.Request) {
	log.Printf("Sending default response...")
	responseWriter.WriteHeader(http.StatusOK)
	fmt.Fprintf(responseWriter, "Ready!")
}

func notFoundHandler(responseWriter http.ResponseWriter, request *http.Request) {
	log.Printf("Not found! %v", request.URL)
	responseWriter.WriteHeader(http.StatusNotFound)
	fmt.Fprintf(responseWriter, "Not Found!")
}

func handleJSONMarshallingError(responseWriter http.ResponseWriter, err error) {
	handleError(responseWriter, err, http.StatusInternalServerError)
}

func handleError(responseWriter http.ResponseWriter, err error, responseCode int) {
	http.Error(responseWriter, err.Error(), responseCode)
}

func getEnvVar(key, defaultVal string) (value string) {
	value = os.Getenv(key)
	if len(value) != 0 {
		log.Printf("Found env variable! [%v = '%v']", key, value)
		return value
	}

	if len(defaultVal) != 0 {
		log.Printf("Defaulted env variable! [%v = '%v']", key, defaultVal)
		return defaultVal
	}

	panic(fmt.Sprintf("Missing env variable! [%v]", key))
}

func main() {
	port := getEnvVar("APP_PORT", "8081")
	dbHost := getEnvVar("APP_MONGO_HOST", "localhost")
	dbPort := getEnvVar("APP_MONGO_PORT", "27017")
	dbName := getEnvVar("APP_MONGO_DB", "FinHisDB")

	log.Printf("Connecting to DB...")
	session, err := mgo.Dial(fmt.Sprintf("%v:%v", dbHost, dbPort))
	if err != nil {
		log.Fatalf("Unable to connect to DB! %v", err)
	}
	defer session.Close()
	db := session.DB(dbName)

	firmHandler := newHandler(db)

	router := mux.NewRouter().StrictSlash(true)
	router.NotFoundHandler = http.HandlerFunc(notFoundHandler)

	router.HandleFunc("/", defaultHandler).Methods("GET")
	router.HandleFunc("/firms", firmHandler.post).Methods("POST")
	router.HandleFunc("/firms", firmHandler.list).Methods("GET")
	router.HandleFunc("/firms/{firm_id}", firmHandler.get).Methods("GET")
	router.HandleFunc("/firms", firmHandler.deleteAll).Methods("DELETE")
	router.HandleFunc("/firms/{firm_id}", firmHandler.delete).Methods("DELETE")

	address := fmt.Sprintf(":%v", port)
	log.Printf("Listening... %v", address)
	http.ListenAndServe(address, router)
}
