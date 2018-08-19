# Financial History Database


## Introduction

The recent financial crisis led the world into what is now called the Great Recession, in reference to the Great Depression of the 1930s.



The EURHISFIRM project aims at designing a world-class research infrastructure to collect, merge, extract, collate, align and share detailed historical high-quality firm level data for Europe.

The goal of the project is to develops innovative tools and sparks the "Big data" revolution in historical social sciences.


## Complementary databases

The USA has been investing enormous resources to build and link databases suited for research over the long run.

The University of Pittsburgh's Collaborative for Historical Information and Analysis (CHIA) is a collaboration of academic and research institutions for the purpose of constructing and populating a world-historical data resource.

The purpose of CHIA is to create a single, comprehensive archive linking an immense range of historical data across space, time, topic, and scale.

The Wharton Research Data Services (WRDS), such as the Compustat database, provides the user access over 250 terabytes of data across multiple disciplines including accounting, banking, economics, insurance and healthcare.

The Center for Research in Security Prices (CRSP), the most widely used database in finance, contains prices and dividends for shares listed on the New York Stock Exchange since 1926.

The use of US data precludes any understanding of the features of the European economy. Because of the USA's hegemony in data production, American companies are frequently and implicitly deemed "representative" or "the norm". Lessons are consequently drawn from their behaviour that are supposed to be applicable everywhere, generating many biases.

Today, only a very few large stand-alone databases have been built so far on Europe by both academic community (e.g. the London Share Prices Database of the London Business School) and private companies (e.g. the US Datastream), without any concern for interoperability.

University of Antwerp: The SCOB database.
Paris School of Economics: the Equipex Data for Financial History.

## Establishing a feature set

The resulting feature set will depend on the potential end-users. These may include:
- Scholars;
- Practitioners;
- Policy makers;
- Regulatory agencies; and
- Society

Focus is placed on financial and economic data that will inform the main feature set of the EURHISFIRM database.

However, given the identified end-users and the discrepancies between European economies, extending the dataset to include more cultural, political and social information may be beneficial to some potential end-users.

When identifying economic and financial data, inspiration is taken from data contained in Yale University's International Center for Finance and Wharton School's Compustat database.

Optimally, we would want a panel data set - a mixture of time-series and cross-sectional data - that contains identification and time-sensitive data about the firms balance sheet and financial position.

The feature set that informs the panel would contain the financial statements of the firms, which would include the firms balance sheet, income statement, statement of cash flows and the statement of changes in equity.

This includes the following collections:

- **Identifying information.** Database UID, company ID, company name, ticker symbol, address, country of headquarters, country of origin, country code, CIGS industry, CIGS sector, CIGS sub-industry, industry classification code.

- **Company description.** Date (year) established, number of employees, market names.

- **Balance sheet items.** Earnings, total assets, liabilities, operating income, operating expenses, debt, equity, deposits (if applicable).

- **Directorate.** Directory of directors.

- **Share characteristics.**  Identity of markets, share par value, dividend payer, dividend yield, liquidity, preference shares, uncalled shares, number of shares, maximum value, share prices, dividend payments, common shares traded, market value and dividends per share.

- **Shareholder characteristics.** Acheson et al. (2017) found that different characteristics of shareholders could be identified and exploited; such as institutional investors, middle class shareholders or rentiers.

- **Supplemental data items.** Source of data.

How this data set is extended may depend on what is needed to be calculated. For example, if the user is interested in comparing companies and industries over time one may want to calculate accounting ratios such as liquidity, profitability and market ratios. This would necessitate the existence of:

 - Net profit, net sales, liquid and illiquid assets

## Extending the database
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

### Foreseeable issues

Problems, such as inconsistencies, may arise when constructing a common data format. For example, there will exist differences in financial and accounting standards, which can change over time and space. Likewise the frequency in which financial statements are recorded may also vary over time and economy. Therefore, data structures may be incomplete when pulled from the database.

To compensate for this it may be good to complement the financial data with metadata on standards for the time periods and economies that have been collected.

## Functionality
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
