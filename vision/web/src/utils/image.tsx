const imageUtil = {

  create: {
    blob: (data: any, type: 'file' | 'binary', returnUrl?: boolean): any => {

      let blob: Blob;
  
      if (type === 'binary') {
        blob = new Blob([data], { type: 'image/png' });
      } else {
        blob = data;
      }
  
      if (returnUrl) {
        let url = URL.createObjectURL(blob);
        return url;
      } else {
        return blob;
      }

    },
    
    base64String: (data: string) => {
      const base64String = btoa(data);
      const url = `data:image/png;base64,${base64String}`;
      return url;
    }
  }

  
}

export default imageUtil;