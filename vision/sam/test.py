from ultralytics.models.sam import Predictor as SAMPredictor

# Create SAMPredictor
overrides = dict(conf=0.25, task='segment', mode='predict', imgsz=1024, model="mobile_sam.pt")
predictor = SAMPredictor(overrides=overrides)

# Segment with additional args
results = predictor(source="claypotRice.jpg", crop_n_layers=1, points_stride=64)
