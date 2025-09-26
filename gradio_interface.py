import gradio as gr
import os
import sys
import tempfile
import shutil
import warnings
from pathlib import Path
from typing import Optional, Tuple, List
import io
from contextlib import redirect_stdout, redirect_stderr

# Import your existing crew components
from src.crew import TacticalCrew, test_enhanced_llm_connectivity

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

class TacticalAnalysisInterface:
    """Gradio interface for the Tactical Analysis Crew"""
    
    def __init__(self):
        self.crew_instance = None
        self.system_status_log = ""
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories for file handling"""
        os.makedirs("temp_uploads", exist_ok=True)
        os.makedirs("output", exist_ok=True)
    
    def capture_llm_status(self) -> str:
        """Capture LLM manager status output"""
        try:
            # Create string buffer to capture output
            output_buffer = io.StringIO()
            
            # Temporarily redirect stdout to capture prints
            with redirect_stdout(output_buffer):
                # Initialize crew to trigger LLM manager status
                test_crew = TacticalCrew()
            
            # Get the captured output
            captured_output = output_buffer.getvalue()
            
            # If no output captured, try to get status directly
            if not captured_output.strip():
                # Create a new crew instance and get status
                temp_crew = TacticalCrew()
                if hasattr(temp_crew, 'llm_manager'):
                    output_buffer_direct = io.StringIO()
                    with redirect_stdout(output_buffer_direct):
                        temp_crew.llm_manager.print_enhanced_status()
                    captured_output = output_buffer_direct.getvalue()
            
            return captured_output if captured_output.strip() else "LLM status not available"
            
        except Exception as e:
            return f"Error capturing LLM status: {str(e)}"
    
    def initialize_crew(self) -> Tuple[bool, str]:
        """Initialize the crew with connectivity testing"""
        try:
            # Capture system status first
            status_buffer = io.StringIO()
            
            with redirect_stdout(status_buffer):
                # Test LLM connectivity first
                connectivity_ok = test_enhanced_llm_connectivity()
                if not connectivity_ok:
                    return False, "LLM connectivity test failed. Check your API keys."
                
                # Initialize crew
                self.crew_instance = TacticalCrew()
            
            # Store the captured status
            self.system_status_log = status_buffer.getvalue()
            
            return True, "Tactical Crew initialized successfully"
            
        except Exception as e:
            return False, f"Failed to initialize crew: {str(e)}"
    
    def get_system_status(self) -> str:
        """Get the current system status"""
        if not self.system_status_log:
            # Try to capture status if not already done
            self.system_status_log = self.capture_llm_status()
        
        return self.system_status_log or "System status not available yet"
    
    def process_file_upload(self, file) -> Optional[str]:
        """Handle file upload and return the saved file path"""
        if file is None:
            return None
        
        try:
            # Create a temporary file path
            file_extension = Path(file.name).suffix
            temp_path = os.path.join("temp_uploads", f"upload_{hash(file.name)}_{os.path.basename(file.name)}")
            
            # Copy uploaded file to temp location
            shutil.copy2(file.name, temp_path)
            return temp_path
            
        except Exception as e:
            print(f"Error processing file upload: {e}")
            return None
    
    def run_analysis(
        self, 
        mission_text: str, 
        uploaded_file, 
        location_input: str,
        progress=gr.Progress()
    ) -> Tuple[str, str, str, str]:
        """Run the tactical analysis with progress tracking"""
        
        try:
            # Initialize crew if not already done
            if self.crew_instance is None:
                progress(0.1, desc="Initializing Tactical Crew...")
                success, message = self.initialize_crew()
                if not success:
                    return message, "", "", ""
            
            progress(0.2, desc="Processing inputs...")
            
            # Determine mission input
            mission_input = None
            
            if uploaded_file is not None:
                # File was uploaded
                file_path = self.process_file_upload(uploaded_file)
                if file_path:
                    mission_input = file_path
                    input_description = f"File: {os.path.basename(file_path)}"
                else:
                    return "Error: Failed to process uploaded file", "", "", ""
            elif mission_text.strip():
                # Text was provided
                mission_input = mission_text.strip()
                input_description = "Direct text input"
            else:
                return "Error: Please provide either text input or upload a file", "", "", ""
            
            # Process location input
            location = location_input.strip() if location_input.strip() else None
            
            progress(0.3, desc="Preparing analysis parameters...")
            
            # Prepare inputs for the crew
            inputs = {
                'mission_input': mission_input,
                'location_input': location
            }
            
            progress(0.4, desc="Starting threat analysis...")
            
            # Run the crew analysis
            result = self.crew_instance.crew().kickoff(inputs=inputs)
            
            progress(0.9, desc="Compiling results...")
            
            # Read the output files
            threat_analysis = self.read_output_file("output/threat_analysis_task.md")
            situation_report = self.read_output_file("output/report_generation_task.md")
            tactical_response = self.read_output_file("output/tactical_response_task.md")
            
            # Create summary
            summary = f"""
            ## Analysis Complete
            
            **Input**: {input_description}
            **Location**: {location or "Auto-detected via IP"}
            **Status**: Analysis completed successfully
            
            **Crew Result Summary**:
            {str(result)[:500]}...
            """
            
            progress(1.0, desc="Analysis complete!")
            
            return summary, threat_analysis, situation_report, tactical_response
            
        except Exception as e:
            error_message = f"Error during analysis: {str(e)}"
            return error_message, "", "", ""
    
    def read_output_file(self, file_path: str) -> str:
        """Read output file with error handling"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"Output file not found: {file_path}"
        except Exception as e:
            return f"Error reading {file_path}: {str(e)}"
    
    def create_interface(self):
        """Create and configure the Gradio interface"""
        
        with gr.Blocks(
            theme=gr.themes.Soft(),
            title="Tactical Analysis Crew",
            css="""
            .gradio-container {
                max-width: 1200px !important;
            }
            .analysis-output {
                max-height: 600px;
                overflow-y: auto;
            }
            """
        ) as interface:
            
            gr.HTML("""
            <div style="text-align: center; padding: 20px;">
                <h1>🎯 Tactical Analysis Crew</h1>
                <p>AI-powered multimodal tactical analysis system</p>
                <p><em>Upload files (images, audio, documents) or provide text for threat analysis</em></p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("<h3>📋 Mission Input</h3>")
                    
                    # Text input
                    mission_text = gr.Textbox(
                        label="Mission Report (Text)",
                        placeholder="Enter your mission report, intelligence briefing, or tactical situation...",
                        lines=8
                    )
                    gr.HTML("<small>Provide text-based mission information</small>")
                    
                    # File upload
                    uploaded_file = gr.File(
                        label="Upload File",
                        file_types=[".txt", ".pdf", ".jpg", ".jpeg", ".png", ".mp3", ".wav", ".m4a"]
                    )
                    gr.HTML("<small>Upload images, audio files, or documents for analysis</small>")
                    
                    gr.HTML("<h3>🗺️ Location Context</h3>")
                    
                    # Location input
                    location_input = gr.Textbox(
                        label="Location (Optional)",
                        placeholder="e.g., 'Valencia, Spain' or '40.4168, -3.7038' or leave empty for auto-detection"
                    )
                    gr.HTML("<small>Provide location name, coordinates, or leave empty for IP-based detection</small>")
                    
                    # Analysis button
                    analyze_btn = gr.Button(
                        "🚀 Run Tactical Analysis",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    gr.HTML("<h3>📊 Analysis Results</h3>")
                    
                    # Results tabs
                    with gr.Tabs():
                        with gr.Tab("🔧 System Status"):
                            system_status_output = gr.Textbox(
                                label="LLM Manager Status",
                                lines=25,
                                max_lines=30,
                                elem_classes=["analysis-output"],
                                interactive=False,
                                show_copy_button=True
                            )
                            refresh_status_btn = gr.Button(
                                "🔄 Refresh Status",
                                variant="secondary",
                                size="sm"
                            )
                        
                        with gr.Tab("📋 Summary"):
                            summary_output = gr.Markdown(
                                label="Analysis Summary",
                                elem_classes=["analysis-output"]
                            )
                        
                        with gr.Tab("🔍 Threat Analysis"):
                            threat_output = gr.Markdown(
                                label="Threat Analysis Report",
                                elem_classes=["analysis-output"]
                            )
                        
                        with gr.Tab("📄 Situation Report"):
                            sitrep_output = gr.Markdown(
                                label="Situation Report",
                                elem_classes=["analysis-output"]
                            )
                        
                        with gr.Tab("⚡ Tactical Response"):
                            tactical_output = gr.Markdown(
                                label="Tactical Response Plan",
                                elem_classes=["analysis-output"]
                            )
            
            # Examples section
            gr.HTML("<h3>💡 Examples</h3>")
            
            gr.Examples(
                examples=[
                    [
                        "Spotted 3 armed personnel with automatic rifles moving east along the main road. Two vehicles (possibly APCs) visible in the distance. Heavy radio chatter detected.",
                        None,
                        "Baghdad, Iraq"
                    ],
                    [
                        "Drone surveillance detected unusual movement patterns near the border crossing. Multiple heat signatures observed during night patrol.",
                        None,
                        "49.0069, 2.5476"
                    ],
                    [
                        "",
                        None,
                        "Valencia, Spain"
                    ]
                ],
                inputs=[mission_text, uploaded_file, location_input],
                label="Try these examples"
            )
            
            # Set up the analysis function
            analyze_btn.click(
                fn=self.run_analysis,
                inputs=[mission_text, uploaded_file, location_input],
                outputs=[summary_output, threat_output, sitrep_output, tactical_output],
                show_progress=True
            )
            
            # Set up system status refresh
            refresh_status_btn.click(
                fn=self.get_system_status,
                inputs=[],
                outputs=[system_status_output]
            )
            
            # Load initial system status
            interface.load(
                fn=self.get_system_status,
                inputs=[],
                outputs=[system_status_output]
            )
            
            # Footer
            gr.HTML("""
            <div style="text-align: center; padding: 20px; margin-top: 40px; border-top: 1px solid #ddd;">
                <p><strong>Tactical Analysis Crew v1.0</strong></p>
                <p>Powered by CrewAI | Multimodal AI Analysis System</p>
                <p><em>⚠️ For demonstration purposes only</em></p>
            </div>
            """)
        
        return interface

def launch_gradio_interface():
    """Launch the Gradio interface"""
    
    print("🚀 Initializing Tactical Analysis Interface...")
    
    # Create interface instance
    interface_manager = TacticalAnalysisInterface()
    
    # Create Gradio interface
    interface = interface_manager.create_interface()
    
    try:
        # Launch with configuration
        interface.launch(
            server_name="0.0.0.0",  # Allow external access
            server_port=7860,
            share=False,  # Set to True if you want a public link
            show_error=True,
            inbrowser=True  # Automatically open browser
        )
    except OSError as e:
        if "address already in use" in str(e).lower() or "errno 48" in str(e).lower():
            print("\n" + "="*70)
            print("❌ ERROR: Port 7860 is already in use")
            print("="*70)
            print("Another Gradio instance or process is using port 7860.")
            print("\nTo kill the process using this port, run one of these commands:")
            print("\n🔧 Option 1 - Kill process by port:")
            print("   lsof -ti:7860 | xargs kill -9")
            print("\n🔧 Option 2 - Find and kill manually:")
            print("   lsof -i:7860")
            print("   kill -9 <PID>")
            print("\n🔧 Option 3 - Kill all Python processes (use with caution):")
            print("   pkill -f python")
            print("\n🔧 Option 4 - Try a different port:")
            print("   Edit the server_port parameter in the code")
            print("="*70)
        else:
            print(f"\n❌ Launch error: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error during launch: {e}")
        raise

if __name__ == "__main__":
    launch_gradio_interface()