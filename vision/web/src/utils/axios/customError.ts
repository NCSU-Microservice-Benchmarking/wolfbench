const getMessage = (error: any): string => {
  let message: string = '';
  let code = error.response.status;

  if (code === 503) {
    message = 'Serivce Unavailable.';
  } else if (code === 500) {
    message = 'Network Error.'
  } else if (code == 400) {
    message = 'Invalid Input.'
  }

  return message;
}