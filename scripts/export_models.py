import os
from pathlib import Path

from humanfriendly.terminal import output
from transformers import AutoConfig, AutoTokenizer, AutoModel
from optimum.exporters.onnx import export
from optimum.onnxruntime import ORTOptimizer
from optimum.onnxruntime.configuration import OptimizationConfig
from onnxruntime import InferenceSession

# Step 1: Load your model and tokenizer
model_name = "lukasellinger/evidence-selection-model"  # Replace with your model
#model = AutoModel.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name, trust_remote_code=True,
                                  add_pooling_layer=False, safe_serialization=True)
config = AutoConfig.from_pretrained(model_name)


onnx_export_dir = "./onnx_model"
optimized_model_dir = "./optimized_onnx_model"

# Ensure directories exist
os.makedirs(onnx_export_dir, exist_ok=True)
os.makedirs(optimized_model_dir, exist_ok=True)
output_dir = Path(onnx_export_dir)

# Step 2: Export Hugging Face model to ONNX
print("Exporting model to ONNX...")
export(
    model=model_name,
    output=output_dir,
    opset=13,  # Ensure this matches your ONNX Runtime version
    config=config
)
print(f"ONNX model exported to: {onnx_export_dir}")

# Step 3: Optimize the ONNX model
print("Optimizing ONNX model...")
optimizer = ORTOptimizer.from_pretrained(onnx_export_dir)
optimization_config = OptimizationConfig(optimization_level=2)  # Choose optimization level
optimizer.optimize(save_dir=optimized_model_dir, optimization_config=optimization_config)
print(f"Optimized model saved to: {optimized_model_dir}")
