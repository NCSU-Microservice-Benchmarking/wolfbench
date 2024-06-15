import { store } from '../redux/store';

import { axiosClient } from '../utils/axios/axiosClient';
import models from '../data/models';

import opentelemetry from '@opentelemetry/api';
import { propagation } from '@opentelemetry/api';
import { W3CBaggagePropagator } from '@opentelemetry/core';
//...

const tracer = opentelemetry.trace.getTracer(
  'example-tracer-web',
  '0.1.0',
);

const requestUtil = {

  image: async (files: File[], setResults: React.Dispatch<React.SetStateAction<ArrayBuffer[]>>) => {

    const span = tracer.startSpan('imageRequest');    

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
      span.end();
      return;
    } catch (error) {
      console.log(error);
      span.end();
      return;
    }
  }

}

export default requestUtil;