export type task = "object_detection" | "semantic_segmentation" | "image_inpainting" 

export interface settings {
  task: task
}
