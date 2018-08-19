# Financial History Database

## Overview

Queen's Management School, Queen's University Belfast, have been awarded a large European Commission Horizon 2020 grant to establish the infrastructure for a pan-EU historical financial database from 1900. As part of this project, we need to survey end-users to establish what they would like to see in an historical financial database and its functionality. Therefore, this repository creates a mock database and API for historical firm-level financial data to be able to demonstrate what firm-level data should be used in the database. Further details on the project can be found on the [CORDIS](https://www.cordis.europa.eu/project/rcn/212955_en.html) and the official [EURHISFIRM](http://eurhisfirm.ue.wroc.pl/) websites. The research proposal can be found in the repository under the [`references`](./references) directory.

In constructing the initial database inspiration is taken from data contained in [Yale University's International Center for Finance](https://som.yale.edu/faculty-research/our-centers-initiatives/international-center-finance/data/historical-financial) and [Wharton School's Research Data Services](https://wrds-web.wharton.upenn.edu/wrds/).

## Technology stack

The mini web application uses [Go](https://golang.org/) as the backend programming language, [MongoDB](https://www.mongodb.com/) as the main database and [mgo](https://github.com/globalsign/mgo) as the MongoDB driver fro Go. Documentation of the RESTful API service is handled by [Swagger](https://swagger.io/). Development is done within a [Docker](https://www.docker.com/) environment. The [`R`](https://www.r-project.org/) programming language is used to generate any synthetic data required for demonstration purposes.

## Data

We use synthetic data for the purpose of this demo. Optimally, we would want a panel data set - a mixture of time-series and cross-sectional data - that contains identification and time-sensitive data about the firms balance sheet and financial position. The feature set that informs the panel would contain the financial statements of the firms, which would include the firms balance sheet, income statement, statement of cash flows and the statement of changes in equity.

The type of data used mimics the [Compustat](https://wrds-www.wharton.upenn.edu/demo/) accounting and financial data model. This includes the following collections:

- **Identifying information.** Database UID, company ID, company name, ticker symbol, address, country of headquarters, country of origin, country code, CIGS industry, CIGS sector, CIGS sub-industry, industry classification code.

- **Company description.** Date (year) established, number of employees, market names.

- **Balance sheet items.** Earnings, total assets, liabilities, operating income, operating expenses, debt, equity, deposits (if applicable).

- **Directorate.** Directory of directors.

- **Share characteristics.**  Identity of markets, share par value, dividend payer, dividend yield, liquidity, preference shares, uncalled shares, number of shares, maximum value, share prices, dividend payments, common shares traded, market value and dividends per share.

- **Shareholder characteristics.** Acheson et al. (2017) found that different characteristics of shareholders could be identified and exploited; such as institutional investors, middle class shareholders or rentiers.

- **Supplemental data items.** Source of data.

Further data included may also depend on what is needed to be calculated. For example, if the user is interested in comparing companies and industries over time one may want to calculate accounting ratios such as liquidity, profitability and market ratios. This would necessitate the existence of:

- Net profit, net sales, liquid and illiquid assets

### Extending the database
_What do end-users want from the database in terms of information?_

Need to define a user requirements documentation, which requires negotiation to determine what is technically and economically feasible. The user requirements documentation should include:

- Operational requirements
- Functional requirements
- Data requirements
- Technical requirements
- Interface requirements
- Environmental requirements
- Availability requirements
- Regulatory requirements
- Migration of any electronic data
- Prioritising requirements (mandatory, beneficial, nice to have)

Ask: One-on-one and group interviews with relevant stakeholders (scholars, practitioners, policy makers, regulatory agencies), questionnaires, prototyping and use cases.

Read: Literature review of how equivalent US databases have been used will highlight case studies.

Requirements should be reviewed and approved by the stakeholders and the subject matter experts. This can be done though:

- Presenting the intent and current state of the database development at conferences.
- Open source some aspects of the development. For example, create a Github account or forum that allows potential users to contribute data sources or suggestions.

## Foreseeable issues

Problems, such as inconsistencies, may arise when constructing a common data format. For example, there will exist differences in financial and accounting standards, which can change over time and space. Likewise the frequency in which financial statements are recorded may also vary over time and economy. Therefore, data structures may be incomplete when pulled from the database.

To compensate for this it may be good to complement the financial data with metadata on standards for the time periods and economies that have been collected.

### Functionality
_What do end-users want from the database in terms of functionality?_

There are further questions to consider: _What is the user community used to with respect to other databases? What is the most useful approach for the type of analysis? What is the most scalable and extendable approach if more data becomes available?_

Within industry the typical way users interact with a database is through the use of an Application Programming Interface (API) call. The API is RESTful in that the queries and path parameters within a URL request are used to access components of data in a predictable way.

For example, querying for the full dataset of all firms would be done with the following request:
```
GET /api/firm-data/all
```
For the full dataset of all firms that existed between 1930 and 1940 we would extend the request to the following:
```
GET /api/firm-data/all?years=[1930,1940]
```
Further, querying for the full data for all firms for each year between 1940 and 1950 that had more than 500 employees would be done with the following API call:
```
GET /api/firm-data/all?years=[1940,1950]&noEmployees=[>,500]
```
Also, if each firm is given a UID, this identifier can be used to query resources attached to the specific firm(s). For example:
```
GET /api/firm-data/uid/abc12345?features=[earnings,noEmployees,noShares]&years=[1999]
```
In each case the API would respond with a JSON structure containing the appropriate data.

## Contact

The best way to troubleshoot or ask for a new feature or enhancement is to create a Github [issue](https://github.com/O1sims/FinHisDB/issues). However, if you have any further questions you can contact [me](mailto:sims.owen@gmail.com) directly.
