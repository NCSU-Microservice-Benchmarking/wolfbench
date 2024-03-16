import { createSlice } from "@reduxjs/toolkit";
import { image } from "../../types/image";

interface imagesState {
  current: null | number, 
  originals: null | image[]
  edited: null | image[],
  results: any
}

const initialState: imagesState = {
  current: null,
  originals: null,
  edited: null,
  results: null
};

export const imagesSlice = createSlice({
  name: 'images',
  initialState,
  reducers: {
    setCurrent: (state, action) => {
      state.current = action.payload;
      return state;
    },
    addToOriginals: (state, action) => {
      let newCurrent = state.originals;
      newCurrent?.push(action.payload);
      state.originals = newCurrent;
      return state;
    },
    setOriginals: (state, action) => {
      state.originals = action.payload;
      return state;
    },
    setEdited: (state, action) => {
      state.edited = action.payload;
      return state;
    },
    setResults: (state, action) => {
      state.results = action.payload;
      return state;
    },
  },
})

export const { setOriginals, setEdited, setResults, setCurrent } = imagesSlice.actions

export default imagesSlice.reducer;