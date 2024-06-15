import './index.css';
import './fonts.css'
import App from './App';

import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './redux/store';

import ScrollToTop from './components/interface/tools/ScrollToTop';

import { Resource } from '@opentelemetry/resources';
import {
  SEMRESATTRS_SERVICE_NAME,
  SEMRESATTRS_SERVICE_VERSION,
} from '@opentelemetry/semantic-conventions';
import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import {BatchSpanProcessor} from '@opentelemetry/sdk-trace-base';
// import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-proto';
import {ZipkinExporter} from '@opentelemetry/exporter-zipkin';

const resource = Resource.default().merge(
  new Resource({
    [SEMRESATTRS_SERVICE_NAME]: 'vision-web',
    [SEMRESATTRS_SERVICE_VERSION]: '0.1.0',
  }),
);

const provider = new WebTracerProvider({
  resource: resource,
});
// const exporter = new ConsoleSpanExporter();
// const exporter = new OTLPTraceExporter({
//   url: 'http://155.138.202.64:4318/v1/traces',
//   headers: {},
// });
const exporter = new ZipkinExporter({
  url: 'http://155.138.202.64:9411/api/v2/spans',
  serviceName: 'vision-web',
  headers: {}, // this header is important for Zipkin to work, as it changes the content type from application/json to xhr (https://github.com/open-telemetry/opentelemetry-js/issues/3062)
});
const processor = new BatchSpanProcessor(exporter);
provider.addSpanProcessor(processor);

provider.register();

const root = createRoot(document.getElementById("root")!);

root.render(
  <Provider store={store}>
    <BrowserRouter>
      <ScrollToTop/>
      <App />
    </BrowserRouter>
  </Provider>
);
