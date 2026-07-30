from lib import global_parameters as gp

def save_parameters(d_parameters):
    input_global = 'Grid_methods/config/global_parameters.txt'
    input_comparison = 'Grid_methods/config/comparison_parameters.txt'
    input_hotspot = 'Grid_methods/config/hotspot_parameters.txt'


    if d_parameters['run_comparison'] == True and d_parameters['run_hotspot'] == False:
        gp.D_PARAMETERS_GLOBAL['choice'] = 'comparison'
    elif d_parameters['run_comparison'] == False and d_parameters['run_hotspot'] == True:
        gp.D_PARAMETERS_GLOBAL['choice'] = 'hotspot'
    elif d_parameters['run_comparison'] == True and d_parameters['run_hotspot'] == True:
        gp.D_PARAMETERS_GLOBAL['choice'] = 'both'

    choice = gp.D_PARAMETERS_GLOBAL['choice']
    if choice in ['comparison', 'both']:
        output_comparison = gp.D_PARAMETERS_COMPARISON['p_output_comparison'] + '/selected_parameters.txt'
        with open(input_global, "r") as f1, open(input_comparison, "r") as f2:
            input_file_1_contents = f1.read()
            input_file_2_contents = f2.read()

    if choice in ['hotspot', 'both']:
        print(gp.D_PARAMETERS_HOTSPOT)
        output_hotspot = gp.D_PARAMETERS_HOTSPOT['p_output_hotspot'] +'/selected_parameters.txt'
        with open(input_global, "r") as f1, open(input_hotspot, "r") as f2:
            input_file_1_contents = f1.read()
            input_file_2_contents = f2.read()

    if choice in ['comparison', 'both']:
        with open(output_comparison, "w") as f_out:
            f_out.write("=== Global Parameters ===\n\n")
            f_out.write(input_file_1_contents)
            f_out.write("\n\n=== Comparison Parameters ===\n\n")
            f_out.write(input_file_2_contents)
    elif choice in ['hotspot', 'both']:
        with open(output_hotspot, "w") as f_out:
            f_out.write("=== Global Parameters ===\n\n")
            f_out.write(input_file_1_contents)
            f_out.write("\n\n=== Hotspot Parameters ===\n\n")
            f_out.write(input_file_2_contents)
