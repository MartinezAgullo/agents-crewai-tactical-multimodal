import os
import tempfile
from typing import Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from pathlib import Path
import subprocess


"""
Tools created for:
    - text-based (DocumentAnalysisTool): analyzes text documents, PDFs, and other written reports for threat intelligence.
    - audio-based (AudioTranscriptionTool): transcribes audio files (mp3, wav, m4a, etc.) into text for threat analysis.
            The parameter NUM_SPEAKERS has been set to 2, which is the common in military conversations.

For image-based inputs, the LLM itself handles it.
"""


# ============================================================================
# INPUT SCHEMAS FOR PYDANTIC VALIDATION
# ============================================================================

class AudioTranscriptionInput(BaseModel):
    """Input schema for audio transcription."""
    audio_path: str = Field(
        ...,
        description="Path to the audio file to transcribe (mp3, wav, m4a, etc.)"
    )


class DocumentAnalysisInput(BaseModel):
    """Input schema for document analysis."""
    document_path: str = Field(
        ...,
        description="Path to the document file to analyze (txt, pdf)"
    )


class InputTypeDeterminerInput(BaseModel):
    """Input schema for input type determination."""
    input_data: str = Field(
        ...,
        description="File path or direct text content to analyze"
    )


# ============================================================================
# AUDIO TRANSCRIPTION TOOL
# ============================================================================

class AudioTranscriptionTool(BaseTool):
    """Transcribes audio files into text with speaker diarization"""
    name: str = "Audio Transcription Tool"
    description: str = (
        "Transcribes audio files (mp3, wav, m4a, etc.) into text for threat analysis. "
        "Now includes speaker diarization using pyannote.audio. "
        "Input: audio_path (string - path to audio file)"
    )
    args_schema: Type[BaseModel] = AudioTranscriptionInput
    
    whisper_model: Optional[Any] = None
    diarization_pipeline: Optional[Any] = None

    def _load_whisper_model(self):
        """Lazy load whisper model only when needed"""
        if self.whisper_model is None:
            try:
                import whisper  # Import only when needed
                self.whisper_model = whisper.load_model("base")
            except ImportError:
                raise ImportError(
                    "Whisper is not installed. Install it with: pip install openai-whisper"
                )
        return self.whisper_model

    def _load_diarization_pipeline(self):
        """Lazy load diarization pipeline only when needed"""
        if self.diarization_pipeline is None:
            try:
                from pyannote.audio import Pipeline  # Import only when needed
                hf_token = os.getenv("HF_TOKEN", None)
                
                if not hf_token:
                    raise ValueError(
                        "HF_TOKEN not found in environment. "
                        "Get your token from https://huggingface.co/settings/tokens"
                    )
                
                print(f"Loading pyannote speaker-diarization model...")
                self.diarization_pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=hf_token
                )
                print("✅ Diarization model loaded successfully")

            except Exception as e:
                error_msg = str(e)
                if "gated" in error_msg.lower() or "private" in error_msg.lower():
                    raise ValueError(
                        "Error accessing the pyannote model. Authentication failed for pyannote model'."
                    )

                raise ImportError(
                    f"Pyannote.audio dependencies not available: {e}\n"
                    "This may be due to PyTorch compatibility issues on your system."
                )
        return self.diarization_pipeline
    
    def _run(self, audio_path: str) -> str:
        try:
            if not os.path.exists(audio_path):
                return f"Error: Audio file not found at {audio_path}"

            # Step 1: Execute diarization
            try:
                diar_pipeline = self._load_diarization_pipeline()
                model = self._load_whisper_model()
            except (ImportError, RuntimeError, OSError) as e:
                return (
                    f"ERROR: Audio transcription dependencies not available\n"
                    f"Details: {str(e)}\n\n"
                    f"WORKAROUND: Audio transcription requires:\n"
                    f"1. Working PyTorch installation\n"
                    f"2. pyannote.audio\n"
                    f"3. HuggingFace token (HF_TOKEN in .env)\n\n"
                )
            
            NUM_SPEAKERS = 2  # Force 2 speakers for military conversations
            diarization = diar_pipeline(audio_path, num_speakers=NUM_SPEAKERS)

            # Step 2: Load Whisper model
            model = self._load_whisper_model()

            # Step 3: Create speaker-labeled text
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                start, end = turn.start, turn.end
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_segment:
                    # Extract corresponding segment
                    subprocess.run([
                        "ffmpeg", "-y", "-i", audio_path,
                        "-ss", str(start), "-to", str(end),
                        "-ar", "16000", "-ac", "1", tmp_segment.name
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    result = model.transcribe(tmp_segment.name, language=None)
                    transcription = result["text"].strip()
                    if transcription:
                        segments.append(f"{speaker}: {transcription}")

            full_transcription = "\n".join(segments)

            formatted_output = f"""
            AUDIO TRANSCRIPTION REPORT:
            ==========================
            Speakers detected: {NUM_SPEAKERS}
            Transcription:
            {full_transcription}
            ==========================
            """
            return formatted_output.strip()

        except Exception as e:
            return f"Error processing audio file: {str(e)}"


# ============================================================================
# DOCUMENT ANALYSIS TOOL
# ============================================================================

class DocumentAnalysisTool(BaseTool):
    name: str = "Document Analysis Tool"
    description: str = (
        "Analyzes text documents, PDFs, and other written reports for threat intelligence. "
        "Input: document_path (string - path to document file)"
    )
    args_schema: Type[BaseModel] = DocumentAnalysisInput
    
    def _run(self, document_path: str) -> str:
        try:
            # Verify file exists
            if not os.path.exists(document_path):
                return f"Error: Document file not found at {document_path}"
            
            file_extension = Path(document_path).suffix.lower()
            
            if file_extension == '.txt':
                content = self._read_text_file(document_path)
            elif file_extension == '.pdf':
                content = self._read_pdf_file(document_path)
            else:
                return f"Unsupported document type: {file_extension}"
            
            formatted_output = f"""
            DOCUMENT ANALYSIS REPORT:
            ========================
            File: {os.path.basename(document_path)}

            Content:
            {content}
            ========================
            """
            return formatted_output.strip()
            
        except Exception as e:
            return f"Error processing document: {str(e)}"
    
    def _read_text_file(self, file_path: str) -> str:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            return f"Error reading text file: {str(e)}"
    
    def _read_pdf_file(self, file_path: str) -> str:
        """Read PDF file using PyPDF2"""
        try:
            import PyPDF2 # another lazy import
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except ImportError:
            return "PDF processing requires PyPDF2: pip install PyPDF2"
        except Exception as e:
            return f"Error reading PDF file: {str(e)}"


# ============================================================================
# INPUT TYPE DETERMINER TOOL
# ============================================================================

class InputTypeDeterminerTool(BaseTool):
    name: str = "Input Type Determiner"
    description: str = (
        "Determines the type of input (text, audio, image, document) and recommends which processing tool to use. "
        "Input: input_data (string - file path or direct text content)"
    )
    args_schema: Type[BaseModel] = InputTypeDeterminerInput
    
    def _run(self, input_data: str) -> str:
        # Check if it's a file path
        if os.path.exists(input_data):
            file_path = input_data
            file_extension = Path(file_path).suffix.lower()
            
            # Audio formats
            if file_extension in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
                return f"""
                INPUT TYPE: AUDIO FILE
                Detected: {file_extension.upper()} audio file
                Recommendation: Use Audio Transcription Tool to convert to text
                File: {os.path.basename(file_path)}
                """
        
            # Document formats
            elif file_extension in ['.txt', '.pdf', '.doc', '.docx']:
                return f"""
                INPUT TYPE: DOCUMENT FILE
                Detected: {file_extension.upper()} document file
                Recommendation: Use Document Analysis Tool to process text content
                File: {os.path.basename(file_path)}
                """
            
            # Image formats
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
                return f"""
                INPUT TYPE: IMAGE FILE
                Detected: {file_extension.upper()} image file
                Recommendation: Process this image yourself or use AddImageTool if available.
                Remember to look for visual threats in military context.
                File: {os.path.basename(file_path)}
                """
            
            # Unknown file type
            else:
                return f"""
                INPUT TYPE: UNKNOWN FILE
                Detected: {file_extension.upper()} file (unsupported format)
                Recommendation: Convert to supported format, provide text directly or directly analyze
                File: {os.path.basename(file_path)}
                """
        
        # Assume it's direct text input
        else:
            word_count = len(input_data.split())
            return f"""
            INPUT TYPE: DIRECT TEXT
            Detected: Text input with {word_count} words
            Recommendation: Process directly for threat analysis
            No additional tools needed - ready for tactical assessment
            """