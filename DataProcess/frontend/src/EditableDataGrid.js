import React, { useState } from 'react'
import { DataGrid } from '@mui/x-data-grid';
import {dateFormatter, durationFormatter, numberFormatter, complexFormatter, stringFormatter} from './DataGridUtils';


const EditableDataGrid = ({ headers, data, onApply }) => {
  
  const [columns, setColumns] = useState(headers);
  const [rows, setRows] = useState(data.map((row, index) => ({
    ...row,
    // Generate unique id based on index to fulfil DataGrid requirment 
    id: ++index,
  })));

  //flag if any field type changed to enable 'Apply' button
  const [typeChanged, setTypeChanged] = useState(false);

  const handleApply = () => {
    const columnsToApply = [];  // Initialize an empty array

    // Iterate through headers and create dictionaries for changed types only
    for (let i = 0; i < headers.length; i++) {
      if (headers[i].type !== columns[i].type) {
        columnsToApply.push({
          field: headers[i].field,
          type: columns[i].type,
        });
      }
    }
    // Pass changed column data to the parent's handler
    onApply(columnsToApply);
  };

  // select element type change handler
  const handleColumnTypeChange = (fieldName, newType) => {
    
    // DataGrid using formatter for each type
    // !! Note: it mimmics the possible pandas series conversion outcome
    const applyFormatter = (type) => {
      const typeMap = {
        'date': (params) => dateFormatter(params, headers),
        'number': numberFormatter,
        'duration': durationFormatter,
        'complex': complexFormatter,
        'string': stringFormatter,
        'category': stringFormatter,
      };
      return typeMap[type] || null; // Use the formatter from the map or no formatter
    }  

    // apply formatter based on new type
    const updatedColumns = columns.map(column => {
      if (column.field === fieldName) {
       return { ...column, type: newType, valueFormatter: applyFormatter(newType) };
      }
      return column;
    });

    const hasTypeChanged = (titles1, titles2) => {
      for (let i = 0; i < titles1.length; i++) {
        if (titles1[i].type !== titles2[i].type) {
          return true; // any headers 'type' is different from initial
        }
      }
      return false; // No difference compare to initial headers
    }

    setTypeChanged(hasTypeChanged(headers, updatedColumns));

    setColumns(updatedColumns);
  };

  //custom header with column type select element
  const renderHeaderWithSelect = (column) => {
    
    const maxLength = 15;  //max header characters length to show and tooltip for full headerName 
    const truncatedHeaderName = column.headerName.length > maxLength ? `${column.headerName.slice(0, maxLength)}...` : column.headerName;

    return (
      <div>
        <span title={column.headerName}>{truncatedHeaderName}</span>
        <select className='ml-1'
          value={column.type}
          onChange={(e) => handleColumnTypeChange(column.field, e.target.value)}
        >
          <option value="string">Text</option>
          <option value="number">Number</option>
          <option value="complex">Complex</option>
          <option value="date">Date</option>
          <option value="duration">Duration</option>
          <option value="category">Category</option>
        </select>
      </div>
    );
  };

  // custom header with dropdown and headerName max length
  const renderCustomHeader = (params) => {
    return <div>{renderHeaderWithSelect(params.colDef)}</div>;
  };


  return (
    <div>
      <button className="btn btn-primary mb-2" disabled={!typeChanged} onClick={handleApply}>
        Apply
      </button>

      <DataGrid
        // Key changes when column's type changed (newType), in SetColumns, it forces DataGrid rerender
        key={JSON.stringify(columns)} 
        rows={rows}
        columns={columns.map((column) => ({
          ...column,
          renderHeader: renderCustomHeader,
          sortable: false, //disable for now. flickers when using select
        }))}

        sx={{
          boxShadow: 2,
          border: 2,
          borderColor: 'primary.light',
          // '& .MuiDataGrid-cell:hover': {
          //   color: 'primary.main',
          // },
          '& .MuiDataGrid-columnHeader': {
            padding: '4px 4px', 
            margin: '1px', 
          },
        }}
        
      />
    </div>
  )
}

export default EditableDataGrid