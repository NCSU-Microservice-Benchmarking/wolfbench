import './Main.css';
import Settings from './Settings';

import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch  } from 'react-redux';
import { RootState } from '../../../redux/store';
import { setOriginals, setCurrent, setResults } from '../../../redux/slices/images';

import MountDisplay from '../../interface/tools/MountDisplay';
import ModalOverlay from '../../interface/ModalOverlay';

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faImage, faPlus } from '@fortawesome/free-solid-svg-icons'

import request from '../../../utils/request';
import imageUtil from '../../../utils/image';
import { image } from '../../../types/image';
import { createId } from '../../../tools/createID';
import sleep from '../../../tools/sleep';
import { setResponse } from '../../../redux/slices/general';

interface MainProps {
  originalFiles: File[],
  setOriginalFiles: React.Dispatch<React.SetStateAction<File[]>>
  resultsFiles: ArrayBuffer[],
  setResultsFiles: React.Dispatch<React.SetStateAction<ArrayBuffer[]>>
}

const Main = (props: MainProps) => {

  const { originalFiles, setOriginalFiles, resultsFiles, setResultsFiles } = props;

  const dispatch = useDispatch();

  const { originals, current } = useSelector((state: RootState) => state.images);
  const { task } = useSelector((state: RootState) => state.settings);
  const { response } = useSelector((state: RootState) => state.general);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  useEffect(() => {
    MountDisplay(undefined, undefined);
  }, []);

  const handleFileSelect = (event: any) => {
    const input = event.target.files;
  
    if (input[0]) {
      const images: image[] = [];
      setOriginalFiles(input);
      for (let i = 0; i < input.length; i++) {

        const reader = new FileReader();
  
        reader.onload = (e) => {
          const base64 = e.target?.result as string;
          const image: image = {
            id: createId(20),
            name: input[i].name,
            type: input[i].type,
            url: imageUtil.create.blob(input[i], 'file', true)!,
            base64: base64,
          };
  
          images.push(image);
  
          // If all images are processed, dispatch the results
          if (images.length === input.length) {
            dispatch(setOriginals(images));
            dispatch(setCurrent(0));
          }
        };
  
        // Read the file as a data URL (Base64)
        reader.readAsDataURL(input[i]);
      }
    }
  };

  const submitRequest = async () => {
    dispatch(setResponse(null));
    if (current !== null) try {
      setIsLoading(true);
      await request.image(originalFiles, setResultsFiles);
      await sleep(300);
      setIsLoading(false);
    } catch {
      setIsLoading(false);
    }
  }

  const clearRequest = () => {
    dispatch(setOriginals(null));
    dispatch(setCurrent(null));
    dispatch(setResponse(null));
    setOriginalFiles([]);
    setResultsFiles([]);
    dispatch(setResults(null));
  }

  return ( 
    <div id="page-content">
      
      <div className="main-pg fade-in-quick">

        {originals && current !== null ?

          (resultsFiles.length > 0 ? 
            <div className='results-display'>

              <div className='results-display-more' style={{display: resultsFiles.length > 1 ? 'flex' : 'none'}}>
                {resultsFiles.map((buffer) => {
                  if (buffer !== resultsFiles[current]) {
                    return (
                      <img src={imageUtil.create.blob(buffer, 'binary', true)} id="queued-img" alt={'Res'}/>
                    )
                  }
                  return null;
                })} 
              </div> 

              <div className='results-display-current fade-in-quick'>
                <img src={imageUtil.create.blob(resultsFiles[current], 'binary', true)} id="results-img" alt="Results"/>
              </div>

            </div>
          :
            <div className="originals-display">

              {isLoading && 
                <ModalOverlay color="white" loader={true}/>
              }

              <div className='originals-display-more' style={{display: originals.length > 1 ? 'flex' : 'none'}}>
                {originals.map((img) => {
                  if (img !== originals[current]) {
                    return (
                      <img src={img.url} id="queued-img" alt={img.name}/>
                    )
                  }
                  return null;
                })} 
                <div id="queued-img-add">
                  <input type="file" name="file" accept="image/*" id="image-input" multiple onChange={handleFileSelect}/>
                  <label htmlFor="image-input" className="image-input-label">
                    <FontAwesomeIcon icon={faPlus}/>
                  </label>
                  </div>
              </div> 

              <div className='original-display-current fade-in-quick'>
                <img src={originals[current].url} id="current-img" alt={originals[current].name}/>
              </div>

            </div>
          )

        :
          (task === 'image_inpainting' ?
            <div className='inpainting-input'>
              <div className="image-input-container">
                <input type="file" name="file" accept="image/*" id="image-input" onChange={handleFileSelect}/>
                <label htmlFor="image-input" className="image-input-label">
                  <h1><FontAwesomeIcon icon={faImage} color='gray'/></h1>
                  <h1>Drag here</h1>
                  <h1>--- or ---</h1>
                  <h1>Click to upload</h1>
                </label>
              </div>

              <div className="image-input-container">
                <input type="file" name="file" accept="image/*" id="image-input" onChange={handleFileSelect}/>
                <label htmlFor="image-input" className="image-input-label">
                  <h1><FontAwesomeIcon icon={faImage} color='gray'/></h1>
                  <h1>Drag here</h1>
                  <h1>--- or ---</h1>
                  <h1>Click to upload</h1>
                </label>
              </div>
            </div>
          
          :
            <div className="image-input-container">
              <input type="file" name="file" accept="image/*" id="image-input" multiple onChange={handleFileSelect}/>
              <label htmlFor="image-input" className="image-input-label">
                <h1><FontAwesomeIcon icon={faImage} color='gray'/></h1>
                {/*<h1>Drag here</h1>
                <h1>--- or ---</h1>*/}
                <h1>Click to upload</h1>
              </label>
            </div>
          )
        }       

        <Settings/>

      </div>


      {response && 
        <div className='response'>
          <h1 style={{color: response.type === 'error' ? 'red' : 'black'}}>
            {response.code ? response.code + ": " : ""} {response.message}
          </h1>
        </div>
      }

      <div className='main-options' style={{visibility: (originals && !isLoading) ? 'visible' : 'hidden', marginTop: !response ? '20px' : '0px', justifyContent: resultsFiles.length ? 'center' : 'space-between'}}>
        <button className="main-options-btn" onClick={submitRequest} style={{display: resultsFiles.length ? 'none' : 'flex'}}>
          Submit
        </button>
        <button className="main-options-btn" onClick={clearRequest}>
          Clear
        </button>
      </div>
      
    </div>
  ); 
}

export default Main;