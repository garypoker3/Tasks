import {parse} from 'duration-fns'
import { formatDuration } from 'date-fns';

export const intlNumberFormatter = new Intl.NumberFormat();

// numeric formatter for 'number' type in DataGrid
export const numberFormatter = (params) => {
  return params.value? intlNumberFormatter.format(params.value) : null;
};

//date formatter for 'date' type in DataGrid
export const dateFormatter = (params, headers) => {
  if(!!!params.value) return null;

  //headers provided if type changed. to compare against initial state
  if(!!headers) {
    const initialType = headers.find(col => col.field === params.field).type;
    
    // number -> date -> number case
    if (initialType === 'number'){
      // number iso 8601 (msec from 1970) to date convert 
      const num = Number(params.value);
      if(!isNaN(num))
        return new Date(num).toLocaleString(); 
    }
    
    // to date conversion
    return new Date(params.value).toLocaleString();
  }

  return params.value.toLocaleString();
  
};

// check if valid ISO8601 duration str
function isValidDurationString(durationString) {
    const pattern = /P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?/i;
    return pattern.test(durationString); // Double-check parsing
}

// DataGrid duration formatter to format 'duration' iso 8601 eg 'P4DT6H30M50S' to 'days, hours, minutes'
export const durationFormatter = (params) => {
    if(!!!params.value)  return null;

    let formattedDuration = 'Invalid Duration';

    //check if valid iso 8601 duration
    if(!isValidDurationString(params.value))  return formattedDuration;

    try {
      const duration = parse(params.value);
      formattedDuration = formatDuration(duration, {
      //Customize units to include based on your needs
      format: ['days', 'hours', 'minutes', ], 
    });
    } catch {
        return formattedDuration;
    }
    
    return formattedDuration? formattedDuration: 'Invalid Duration';
  }

  //format complex type {real, imag}
  export const complexFormatter = (params) => {

    if(params.value?.real === undefined){
      const num = Number(params.value);
      if(!isNaN(num))
        return `${intlNumberFormatter.format(num)}+0j`;  

      return '0+0j';
    }


    return params.value? `${intlNumberFormatter.format(params.value.real)}+${intlNumberFormatter.format(params.value.imag)}j` : null;
  }

   //format Text (string) type
   export const stringFormatter = (params) => {
    // complex number 
    if(params.value?.real !== undefined) {
       return `${intlNumberFormatter.format(params.value.real)}+${intlNumberFormatter.format(params.value.imag)}j`;
    }
    return params.value;
  }