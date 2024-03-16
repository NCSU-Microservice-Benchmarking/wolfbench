import { createSlice } from "@reduxjs/toolkit";
import models from "../../data/models";
import { task } from "../../types/settings";

interface settingsState {
  task: task,
  model: string
}

const initialState: settingsState = {
  task: 'object_detection',
  model: models['object_detection'].models[0].name
};

export const settingsSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setTask: (state, action) => {
      state.task = action.payload;
    },
    setModel: (state, action) => {
      state.model = action.payload;
      return state;
    },
    resetModel: (state) => {
      state.model = models[state.task].models[0].name;
      return state;
    }
  },
})

export const { setTask, setModel, resetModel } = settingsSlice.actions

export default settingsSlice.reducer;