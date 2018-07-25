# Financial History Database

## Overview

Queen's Management School, Queen's University Belfast, have been awarded a large European Commission Horizon 2020 grant to establish the infrastructure for a pan-EU historical financial database from 1900. As part of this project, we need to survey end-users to establish what they would like to see in an historical financial database and its functionality. Therefore, this repository creates a mock database and API for historical firm-level financial data to be able to demonstrate what firm-level data should be used in the database. Further details on the project can be found on the [CORDIS](https://www.cordis.europa.eu/project/rcn/212955_en.html) and the official [EURHISFIRM](http://eurhisfirm.ue.wroc.pl/) websites. The research proposal can be found in the repository under the [`references`](./references) directory.

In constructing the initial database inspiration is taken from data contained in [Yale University's International Center for Finance](https://som.yale.edu/faculty-research/our-centers-initiatives/international-center-finance/data/historical-financial) and [Wharton School's Research Data Services](https://wrds-web.wharton.upenn.edu/wrds/).

## Technology stack

The mini web application uses [Go](https://golang.org/) as the backend programming language, [MongoDB](https://www.mongodb.com/) as the main database and [mgo](https://github.com/globalsign/mgo) as the MongoDB driver fro Go. Documentation of the RESTful API service is handled by [Swagger](https://swagger.io/). Development is done within a [Docker](https://www.docker.com/) environment. The [`R`](https://www.r-project.org/) programming language is used to generate any synthetic data required for demonstration purposes.

## Data

We use synthetic data for the purpose of this demo. The type of data used mimics the [Compustat](https://wrds-www.wharton.upenn.edu/demo/) accounting and financial data model. This includes the following collections:

- **Identifying information.** Company ID, company name, ticker symbol, address, country code, CIGS industry, CIGS sector, CIGS sub-industry, industry classification code.

- **Company description.** Year established, size, market names, foreign company, US company.

- **Balance sheet items.** Earnings, liquid and illiquid assets, liabilities, deposits (if applicable).

- **Directorate.** Directory of directors.

- **Share characteristics.** Shareholder characteristics, identity of markets, share par value, dividend payer, dividend yield, liquidity, preference shares, uncalled shares, number of shares, max. value, share prices, dividend payments, common shares traded, market value and dividends per share.

- **Supplemental data items.** Merged.

## Contact

The best way to troubleshoot or ask for a new feature or enhancement is to create a Github [issue](https://github.com/O1sims/FinHisDB/issues). However, if you have any further questions you can contact [me](mailto:sims.owen@gmail.com) directly.
