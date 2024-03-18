
## Project Overview:

This web app processes CSV or Excel files, focusing on Pandas Series data type inference and conversion. Users can choose and upload a file to process and view the converted data displayed in a DataGrid with the data type shown for each column.

For a quick test upon first loading the page processes a pre-set data sample. This allows them to see how different data types are displayed.

For each column, users can change the inferred data type using a dropdown menu with predefined options. The column will dynamically display the potential outcome of the data conversion.

    Note : 
     Explicit conversion is always applied to the initial CSV/Excel data.
     
     Some custom data type conversions are implemented. For example, it can convert numbers to datetime using Unix Time (or Unix Epoch Time). It also supports complex type conversions, such as transforming the string "8+8.8" into a complex number. This allows users to override the inferred data types for specific columns.
     
     The DataGrid formatters are implemented on the client to mimic possible Pandas conversion outcomes, but to see the real conversion result, the user should click 'Apply'.

After changing column types, users can click the "Apply" button to process the data conversion on the backend and reload the new, converted data into the DataGrid.

   ***Data type inference algorithm:***

By default, if conversion can be successful for 80% of the data in a column, the column will be converted to that data type unless directly specified by user using 'Apply'. The conversion attempts follow this order:

1. Numeric
2. Complex
3. Datetime
4. Timedelta
5. Category

#
#
## Getting Started with DataProcess App

The project comprises: a backend server app and a frontend UI, residing in separate backend and frontend folders accordingly.

##
### Backend Django App

Make sure your Python and Django evnironment is set up

#### `pip install django`

**————————install dependencies ———————**

#### `pip install djangorestframework` 
#### `pip install django-cors-headers`

#### `pip install pandas`
#### `pip install numpy`

#### to read excel file:
#### `pip install openpyxl` 

### apply migration:
#### `python manage.py migrate`

##### to run tests in backend/apiapp/data_test.py requires pytest and faker for test data generation
#### `pip install pytest`
#### `pip install faker`
##### ! if you want to run tests not from Tests Explorer but from command line, run `pytest` from root project directory as there are hardcoded path to backend/apiapp/TestData folder.


##
*start the server:*
In the project directory/backend, run
#### `python manage.py runserver`

#
#
### Frontend React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

In the project directory/frontend run:

#### `npm install`

#### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

