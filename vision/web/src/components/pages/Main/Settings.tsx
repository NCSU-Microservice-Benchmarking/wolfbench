import './Settings.css';
import React, { useEffect } from 'react';
import { useSelector, useDispatch  } from 'react-redux';
import { RootState } from '../../../redux/store';

import models from '../../../data/models';
import { resetModel, setModel, setTask } from '../../../redux/slices/settings';

const Settings = () => {

  const dispatch = useDispatch();

  const { originals, current } = useSelector((state: RootState) => state.images);
  const { task, model } = useSelector((state: RootState) => state.settings);

  //reset model variable when task is changed
  useEffect(() => {
    dispatch(resetModel());
  }, [task, dispatch]);

  const changeTask = (task: string) => {
    dispatch(setTask(task));
  }

  const changeModel = (model: string) => {
    dispatch(setModel(model));
  }

  return ( 
    <div className="settings-container">

      <h2>
        <i className="fa-solid fa-gear" style={{marginRight: '10px', color: 'black'}}></i>
        {current !== null && originals![current].name}
      </h2>

      <div className='seperator' style={{height: '2px', background: 'gray', marginBottom: '20px'}}></div>

      <div className='setting'>
        <div className='setting-header'>
          <h1>
            <i className="fa-light fa-list-check" style={{marginRight: '5px'}}></i>
            Task
          </h1>
        </div>
        <div className="task-options">
          {Object.values(models).map((task_: any, index: number) => {
            return (
              <div className='task-options-item' 
                key={index}
                style={{background: Object.keys(models)[index] === task ? '#f19696' : 'inherit'}} 
                onClick={() => changeTask(Object.keys(models)[index])}
              >
                <i className={`fa-light ${task_.icon}`} style={{marginRight: '5px'}}/>
                <h1>
                  {task_.short_name}
                </h1>
              </div>
            )
          })}
        </div>
      </div>

      <div className='setting'>
        <div className='setting-header'>
            <h1>
              <i className="fa-light fa-diagram-subtask" style={{marginRight: '5px'}}></i>
              Model
            </h1>
        </div>
        <div className="model-options">
          {task && models[task].models.map((model_: any, index: number) => {
            return (
              <div className='model-options-item'
                key={index} 
                style={{background: model === model_.name ? '#f19696' : 'inherit'}}
                onClick={() => changeModel(model_.name)}
              >
                {model_.img && <img className="model-option-item-img" src={model_.img} alt={model_.name} style={{}}/>}
                <h1>
                  {model_.name}
                </h1>
              </div>

            )
          })}
        </div>
      </div>

      {/*<div className='setting'>
        <div className='setting-header' style={{textAlign: 'right'}}>
          <h1>
            <i className="fa-light fa-sliders" style={{marginRight: '5px', color: 'black'}}></i>
            Settings
          </h1>
        </div>
        <div className="slider-options">
          <div className="slidecontainer">
            <input type="range" min="1" max="100" className="slider" id="myRange"/>
          </div>
          <div className="slidecontainer">
            <input type="range" min="1" max="100" className="slider" id="myRange"/>
          </div>
          <div className="slidecontainer">
            <input type="range" min="1" max="100" className="slider" id="myRange"/>
          </div>
        </div>
        </div>*/}
        
    </div>
  ); 
}

export default Settings;



