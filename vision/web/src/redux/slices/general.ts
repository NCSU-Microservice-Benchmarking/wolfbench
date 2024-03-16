import { createSlice } from "@reduxjs/toolkit";

interface generalState {
  language: string,
  response: null | {
    type: string,
    message: string,
    code: number
  }
}

const initialState: generalState = {
  language: 'en-US',
  response: null,
};

export const generalSlice = createSlice({
  name: 'general',
  initialState,
  reducers: {
    setLanguage: (state, action) => {
      state.language = action.payload;
      return state;
    },
    setResponse: (state, action) => {
      state.response = action.payload;
      return state;
    },
  },
})

export const { setLanguage, setResponse } = generalSlice.actions

export default generalSlice.reducer;