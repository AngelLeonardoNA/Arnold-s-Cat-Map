import os
try:
    from PIL import Image
except ImportError:
    print("La biblioteca Pillow no está instalada.")
    print("Por favor, instálala ejecutando: pip install Pillow")
    exit()

def apply_single_arnold_cat_iteration(input_image_path, output_image_path):
    """
    Aplica una única iteración de la transformación Arnold's Cat Map a una imagen
    y guarda el resultado. La imagen de entrada se convierte a RGB.
    Devuelve True si la operación fue exitosa, False en caso contrario.
    """
    try:
        with Image.open(input_image_path) as img:
            image_to_process = img.convert("RGB")
            
            width, height = image_to_process.size

            if width != height:
                print(f"Error: La imagen en '{input_image_path}' no es cuadrada ({width}x{height}).")
                if input_image_path != output_image_path:
                    img.save(output_image_path)
                return False

            canvas = Image.new(image_to_process.mode, (width, height))

            for x in range(width):
                for y_math in range(height):
                    
                    y_pil_get = height - 1 - y_math
                    
                    pixel_value = image_to_process.getpixel((x, y_pil_get))

                    nx_math = (2 * x + y_math) % width
                    ny_math = (x + y_math) % height
                    
                    ny_pil_put = height - 1 - ny_math
                    
                    canvas.putpixel((nx_math, ny_pil_put), pixel_value)
            
            canvas.save(output_image_path)
            return True
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de imagen en '{input_image_path}'.")
        return False
    except Exception as e:
        print(f"Error procesando la imagen '{input_image_path}': {e}")
        return False

def run_arnold_cat_map_pipeline(initial_image_path, num_iterations, keep_all_files=False, 
                                output_name_template="arnold_cat-{name}-{index}.png"):
    """
    Orquesta la aplicación de Arnold's Cat Map por múltiples iteraciones.
    """
    if not os.path.exists(initial_image_path):
        print(f"Error: La imagen inicial '{initial_image_path}' no existe.")
        return None

    try:
        with Image.open(initial_image_path) as img_check:
            if img_check.width != img_check.height:
                print(f"Error: La imagen inicial '{initial_image_path}' debe ser cuadrada.")
                print(f"Dimensiones actuales: {img_check.width}x{img_check.height}")
                return None
    except Exception as e:
        print(f"Error al verificar la imagen inicial: {e}")
        return None

    image_file_stem = os.path.splitext(os.path.basename(initial_image_path))[0]
    
    current_processing_input_path = initial_image_path
    final_image_path = initial_image_path

    if num_iterations == 0:
        print("Número de iteraciones es 0. No se aplicarán transformaciones.")
        return Image.open(initial_image_path)


    for i in range(1, num_iterations + 1):
        generated_output_path = output_name_template.format(name=image_file_stem, index=i)
        
        print(f"Iteración {i}: Procesando '{current_processing_input_path}' -> Guardando en '{generated_output_path}'")
        
        success = apply_single_arnold_cat_iteration(current_processing_input_path, generated_output_path)
        if not success:
            print(f"Fallo en la iteración {i}. Abortando.")
            return None

        if not keep_all_files and current_processing_input_path != initial_image_path:
            if os.path.exists(current_processing_input_path):
                os.remove(current_processing_input_path)
        
        current_processing_input_path = generated_output_path
        final_image_path = generated_output_path

    if os.path.exists(final_image_path):
        return Image.open(final_image_path)
    else:
        print(f"Error: No se encontró la imagen final esperada en '{final_image_path}'.")
        return None

if __name__ == "__main__":
    print("Transformación Arnold's Cat Map")
    print("---------------------------------")

    initial_path = ""
    while True:
        initial_path_input = input("Ingresa la ruta a tu imagen (debe ser cuadrada):\n\t").strip()
        if not initial_path_input:
            print("La ruta no puede estar vacía.")
            continue
        if os.path.exists(initial_path_input):
            try:
                with Image.open(initial_path_input) as img:
                    if img.width == img.height:
                        initial_path = initial_path_input
                        break
                    else:
                        print(f"Error: La imagen no es cuadrada ({img.width}x{img.height}). Por favor, proporciona una imagen cuadrada.")
            except Exception as e:
                print(f"No se pudo abrir o verificar la imagen: {e}. Intenta con otra ruta.")
        else:
            print("No se encontró la imagen en la ruta especificada. Intenta de nuevo.")
            
    iterations = 0
    while True:
        try:
            iterations_input = input("Ingresa el número de iteraciones a aplicar (ej. 3):\n\t").strip()
            iterations = int(iterations_input)
            if iterations >= 0:
                break
            else:
                print("El número de iteraciones no puede ser negativo.")
        except ValueError:
            print("Entrada inválida. Por favor, ingresa un número entero para las iteraciones.")

    keep_all = False
    if iterations > 0:
        while True:
            keep_all_input = input("¿Conservar todos los archivos de imagen intermedios? (si/no):\n\t").strip().lower()
            if keep_all_input in ['si', 's']:
                keep_all = True
                break
            elif keep_all_input in ['no', 'n']:
                keep_all = False
                break
            else:
                print("Respuesta inválida. Por favor, escribe 'si' o 'no'.")

    print(f"\nProcesando '{initial_path}' con {iterations} iteraciones...")
    
    final_result_image = run_arnold_cat_map_pipeline(initial_path, iterations, keep_all_files=keep_all)

    if final_result_image:
        print("\n¡Transformación completada!")
        
        image_file_stem_final = os.path.splitext(os.path.basename(initial_path))[0]
        if iterations > 0:
            final_saved_path = f"arnold_cat-{image_file_stem_final}-{iterations}.png"
            print(f"La imagen final procesada se ha guardado como '{final_saved_path}' (o similar).")
        else:
            print(f"La imagen original '{initial_path}' no fue modificada (0 iteraciones).")

        if not keep_all and iterations > 1:
             print("Los archivos intermedios (si los hubo) han sido eliminados.")
        
        print("Mostrando la imagen resultante...")
        try:
            final_result_image.show()
        except Exception as e:
            print(f"No se pudo mostrar la imagen automáticamente: {e}")
            print("Puedes encontrar la imagen final en la ruta mencionada.")
    else:
        print("\nLa transformación falló o fue interrumpida.")