from pathlib import Path
from xdmf_converter.xdmf_converter import xdmf_convert

# Source folder and source file name
source_folder = str(Path(__file__).parent)

# xdmf_convert(source_folder, '/density', '.xdmf', g_name='density')

xdmf_convert(source_folder, '/test_am_multiple_layer', '.xdmf', g_name='displacement')