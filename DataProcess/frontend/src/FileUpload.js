import React, { useState, useEffect } from 'react';
import axios from 'axios';
import EditableDataGrid from './EditableDataGrid';
import {durationFormatter, complexFormatter, numberFormatter, dateFormatter} from './DataGridUtils';

const FileUpload = () => {

  const test_csv = 
 `Time,Name,Birthdate,Score,Grade,Sum
 01:30:00,Alice,1/01/1990,1709991489000,A,1+2E7j
 00:15:42,Bob,2023-09-15 12:30:45-05:00,75,B,2+3.33j
 02:00:00,Charlie,3/03/1992,85,A,3+2
 102:30:50,David,4/04/1993,70,B,7j
 01:30:00,P0DT1H30M,Not Available,Not Available,A,8
 nan,2+3j,2023-09-15 12:30:45+00:00,1500,B,abc
  `;

  //initial state: set test csv data
  const [selectedFile, setSelectedFile] = useState(new File([test_csv], 'sample_data.csv'));
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [htmlErrorMessage, setHtmlErrorMessage] = useState('');
  const [responseData, setResponseData] = useState(null);
  const [columnsDef, setColumnsDef] = useState(null);
  
  useEffect(() => {
    handleUpload(); // For test purpose to load Call handleUpload function when the component mounts
  }, []); // Empty dependency array ensures the effect runs only once


  const cleanUp = () => {
    setErrorMessage('');
    setHtmlErrorMessage('');
    setUploadMessage('');
    setResponseData(null);
  };


  // formatters used for initial DataGrid state
  const applyFormatter = (type) => {
    const typeMap = {
      'date': (params) => dateFormatter(params, null),
      'number': numberFormatter,
      'duration': durationFormatter,
      'complex': complexFormatter,
    };
    return typeMap[type] || null; // Use the formatter from the map or no formatter
  }  

  const mapColumnType = (pandasType) => {
    if (pandasType.startsWith('int') || pandasType.startsWith('uint') || pandasType.startsWith('float')) {
      return 'number'; // Map all integer and float types to 'number'
    } else if (pandasType.startsWith('complex')) {
      return 'complex'; 
    } else if (pandasType.startsWith('datetime64[ns')) {
      return 'date'; // Map 'datetime64[ns]' and datetime64[ns, <tz>] to 'date'
    } else if (pandasType === 'timedelta64[ns]') {
      return 'duration'; 
    } else if (pandasType === 'category') {
      return 'category'; 
    } else {
      // Return string as default
      return 'string';
    }
  };

  const handleFileChange = (event) => {
    cleanUp();
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    cleanUp();
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    axios.post(
       // rest api url hardcoded
      'http://localhost:8000/api/process-file/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          if (percentCompleted === 100)
            setUploadMessage('Processing file on server...');
          else
            setUploadMessage(`Uploading to server... ${percentCompleted}%`);
        },
      }
    ).then(handleResponse).catch(handleException).finally(setIsUploading(false));
  };

  const handleException = ex => {
    console.error(ex);
    if (ex.response){
      if (ex.response.data.error)
        setErrorMessage(`${ex.response.data.error}`);
      else{
        //unhandled exception
        setHtmlErrorMessage(`${ex.response.data}`);
      }
    }
    else
      setErrorMessage('Failed. Try again.');
  }

  const handleResponse = response => {
    setUploadMessage('Finished');

    const columns_def = response.data.columns_def;
    const data = JSON.parse(response.data.data);

    //extra fields to make  dataFrame columns definition and presentation compatible with DataGrid
    const columns_def_mapped = columns_def.map(item => ({
      ...item,
      headerName: item.field, // headerName with the same value as field
      type: mapColumnType(item.df_type),
      // adjust width:  item.width is char length + select element. choose header if it's longer
      width: item.field.length >= item.width ? item.field.length * 10 + 100 : item.width * 10 + 100,
      minWidth: 150,
      maxWidth: 500,
      align: 'center', headerAlign: 'center',
      //formatter to format data in DataGrid
      valueFormatter: applyFormatter(mapColumnType(item.df_type)),
    }));

    // Convert date fields (json) to Date objects to be presented in DataGrid
    data.forEach(row => {
      columns_def_mapped.forEach(column => {
        if (column.type === 'date' && !!row[column.field]) {
          row[column.field] = new Date(row[column.field]);
        }
      });
    });

    setColumnsDef(columns_def_mapped);
    setResponseData(data);
    setUploadMessage('');

  };

  // apply conversion event from 'child' EditableDataGrid component 
  // post to api method on server
  const handleApplyConversion = async (cols) => {
    cleanUp();
    setIsUploading(true);
    axios.post(
      // rest api url hardcoded
     'http://localhost:8000/api/apply-conversion/',
      cols
   ).then(handleResponse).catch(handleException).finally(setIsUploading(false));
  };

  return (
    <div className="d-flex justify-content-start align-items-start flex-wrap m-5">

      <input type="file" onChange={handleFileChange} disabled={isUploading}/>
      <button className="btn btn-primary mr-5" onClick={handleUpload} disabled={!!!selectedFile || isUploading}>
        {isUploading ? 'Please wait...' : 'Upload File'}
      </button>

      {errorMessage && <p className="text-danger mb-0">Error: {errorMessage}</p>}
      {/* handle django exception html response Debug=True */}
      {htmlErrorMessage && <div dangerouslySetInnerHTML={{ __html: htmlErrorMessage }} />}
      {!!!errorMessage && !!!htmlErrorMessage && uploadMessage && <p>{uploadMessage}</p>}

      <div className='mt-3' style={{ height: '100%', width: '100%' }}>
        { responseData && <EditableDataGrid headers={columnsDef} data={responseData} onApply={handleApplyConversion}/> }
      </div>
    </div>
  );
};

export default FileUpload;
