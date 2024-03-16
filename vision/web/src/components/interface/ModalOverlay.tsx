import React from "react";

const ModalOverlay = (props: any) => {

  const { opacity, fadeIn, borderRadius, color, loader } = props;

  return (
    <div id="modal-overlay" 
      style={{opacity: opacity ? opacity : '0.8', borderRadius: borderRadius ? borderRadius : 'none', background: color}}
      className={fadeIn && 'fade-in-modal'}
    >
      {loader && <div id="basic-loader" style={{zIndex: '12'}}></div>}
    </div>
  );
}
 
export default ModalOverlay;