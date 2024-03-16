import { configureStore } from '@reduxjs/toolkit';

import generalReducer from './slices/general';
import settingsReducer from './slices/settings';
import imagesReducer from './slices/images';

const reducer = {
  general: generalReducer,
  settings: settingsReducer,
  images: imagesReducer
}

export const store = configureStore({
  reducer: reducer,
  devTools: true,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
  }),
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>
// Inferred type: {posts: PostsState, comments: CommentsState, users: UsersState}
export type AppDispatch = typeof store.dispatch