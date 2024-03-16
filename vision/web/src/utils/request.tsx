import { store } from '../redux/store';

import { axiosClient } from '../utils/axios/axiosClient';
import models from '../data/models';

const requestUtil = {

  image: async (files: File[], setResults: React.Dispatch<React.SetStateAction<ArrayBuffer[]>>) => {

    const formData = new FormData();

    const { current } = store.getState().images;
    const { model, task } = store.getState().settings;

    formData.append('image', files[current!]);
    //formData.append('mask', current); 
    
    let path: string = models[task].models.find((model_) => model_.name === model)?.path!;
    
    try {
      const response = await axiosClient.post(path, formData);
      console.log(response.data);
      setResults([response.data]);
      return;
    } catch (error) {
      console.log(error);
      return;
    }
  }

}

export default requestUtil;