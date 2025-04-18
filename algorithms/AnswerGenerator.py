from utils.Prompts import AnswerGeneratorPrompt
from utils.LocalModelGenerator import LocalModelGenerator
from utils.APIGenerator_aisuite import APIGenerator_aisuite
from utils.APIGenerator_request import APIGenerator_request
import yaml
import logging
import pandas as pd

class AnswerGenerator:
    '''
    Answer Generator is a class that generates answers for given questions.
    '''
    def __init__(self, config: dict):
        self.config = config
        self.prompt = AnswerGeneratorPrompt()
        self.model_generator = self.__init_model__()
        self.input_file = self.config.get("input_file")
        self.output_file = self.config.get("output_file")
        self.input_prompt_key = self.config.get("input_prompt_key", "prompt")
        self.output_text_key = self.config.get("output_text_key", "response")

        # Ensure required paths and keys are provided
        if not self.input_file or not self.output_file:
            raise ValueError("Both input_file and output_file must be specified in the config.")

    def __init_model__(self):
        '''
        Initialize the model generator based on the configuration.
        '''
        generator_type = self.config.get("generator_type", "local").lower()
        if generator_type == "local":
            return LocalModelGenerator(**self.config.get("local_model_generator", {}))
        elif generator_type == "aisuite":
            return APIGenerator_aisuite(**self.config.get("aisuite_model_generator", {}))
        elif generator_type == "request":
            return APIGenerator_request(**self.config.get("request_model_generator", {}))
        else:
            raise ValueError(f"Invalid generator type: {generator_type}")
    
    def run(self):
        '''
        Runs the answer generation process, reading from the input file and saving results to output.
        '''
        # Read input file: only accept jsonl format
        dataframe = pd.read_json(self.input_file, lines=True)
        
        # Ensure the input and output keys are correctly set
        self._validate_dataframe(dataframe)

        # Extract the prompts and generate answers
        user_prompts = dataframe[self.input_prompt_key].tolist()
        answers = self.model_generator.generate_text(user_prompts)

        # Save the generated answers to the output file
        dataframe[self.output_text_key] = answers
        dataframe.to_json(self.output_file, orient="records", lines=True)

    def _validate_dataframe(self, dataframe: pd.DataFrame):
        '''
        Helper method to validate the input dataframe columns.
        '''
        # Check if the input prompt key exists in the dataframe
        if self.input_prompt_key not in dataframe.columns:
            raise ValueError(f"input_prompt_key: {self.input_prompt_key} not found in the dataframe.")
        
        # Check if the output text key already exists in the dataframe
        if self.output_text_key in dataframe.columns:
            raise ValueError(f"Found {self.output_text_key} in the dataframe, which would overwrite an existing column. Please use a different output_key.")
