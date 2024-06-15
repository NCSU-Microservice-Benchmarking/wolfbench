import { store } from '../redux/store';

import { axiosClient } from '../utils/axios/axiosClient';
import models from '../data/models';

import opentelemetry from '@opentelemetry/api';
import { context, propagation } from '@opentelemetry/api';
// import { TextMapSetter } from '@opentelemetry/api';
//...

const tracer = opentelemetry.trace.getTracer(
  'example-tracer-web',
  '0.1.0',
);

const requestUtil = {

  image: async (files: File[], setResults: React.Dispatch<React.SetStateAction<ArrayBuffer[]>>) => {

    tracer.startActiveSpan('send_image_request', async (span) => {

      // get the current context
      const baggage = propagation.createBaggage({
        'context': {value: 'vision-microservice-web'}
      });
      const ctxWithBaggage = propagation.setBaggage(context.active(), baggage);
      console.log('Active Baggage:', propagation.getBaggage(ctxWithBaggage));
      // set the context
      context.with(ctxWithBaggage, async () => {
        // do something
        
        const output = {};
        propagation.inject(ctxWithBaggage, output);
        console.log('output', output);
        
        // set the string as a header
        axiosClient.defaults.headers.common['traceparent'] = output['traceparent'];
        axiosClient.defaults.headers.common['tracestate'] = output['tracestate'] || '';
        axiosClient.defaults.headers.common['baggage'] = output['baggage'] || '';

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
      });
    });


  }

}

export default requestUtil;