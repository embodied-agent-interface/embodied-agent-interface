cd "$(dirname "$0")"
python agent_eval.py --mode output --eval_type action --model_name gpt-4o-2024-05-13 --resource_dir resources/ --helm_dir helm/ --dataset virtualhome --dataset_dir dataset/ --prompt_dir prompts/ --output_dir output/ --scene_id 1