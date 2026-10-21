import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ShieldingCalcGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator Kedokteran Nuklir")
        self.root.geometry("1100x750")
        
        # --- DATA BASE ---
        self.isotopes = {
            "Tc-99m": {"gamma_coef": 0.022, "energy": "140 keV"},
            "I-131":  {"gamma_coef": 0.052, "energy": "364 keV"},
            "F-18":   {"gamma_coef": 0.135, "energy": "511 keV"},
            "Lu-177": {"gamma_coef": 0.008, "energy": "208 keV"},
            "Ga-68":  {"gamma_coef": 0.150, "energy": "511 keV"}
        }
        
        # Parameter alfa untuk setiap material dan isotop
        self.materials_alfa = {
            "Timbal (Pb)":  {"alfa_Tc99m": 2.558, "alfa_Lu177": 0.3855, "alfa_I131": 0.1082, "alfa_F18": 0.166,"alfa_Ga68": 0.166},
            "Beton_rendah": {"alfa_Tc99m": 0.02047, "alfa_Lu177": 0.01615, "alfa_I131": 0.01363, "alfa_F18": 0.01126,"alfa_Ga68": 0.01126},
            "Beton_tinggi": {"alfa_Tc99m": 0.03102, "alfa_Lu177": 0.02477, "alfa_I131": 0.02062, "alfa_F18": 0.01558,"alfa_Ga68": 0.01558},
            "Baja":         {"alfa_Tc99m": 0.1581, "alfa_Lu177": 0.0797, "alfa_I131": 0.05786, "alfa_F18": 0.05032, "alfa_Ga68": 0.05032}
        }
        
        # Parameter beta untuk setiap material dan isotop
        self.materials_beta = {
            "Timbal (Pb)":  {"beta_Tc99m": 1.010, "beta_Lu177": 1.071, "beta_I131": 0.2072, "beta_F18": -0.02184,"beta_Ga68": -0.02184},
            "Beton_rendah": {"beta_Tc99m": -0.01122, "beta_Lu177": -0.007056, "beta_I131": -0.007896, "beta_F18": -0.006463, "beta_Ga68": -0.006463},
            "Beton_tinggi": {"beta_Tc99m": -0.01729, "beta_Lu177": -0.001173, "beta_I131": -0.01220, "beta_F18": -0.008775,"beta_Ga68": -0.008775},
            "Baja":         {"beta_Tc99m": -0.04346, "beta_Lu177": 2.243, "beta_I131": -0.02574, "beta_F18": -0.02632,"beta_Ga68": -0.02632}
        }

        # Parameter gamma untuk setiap material dan isotop
        self.materials_gamma = {
            "Timbal (Pb)":  {"gamma_Tc99m": 4.344, "gamma_Lu177": 0.2822, "gamma_I131": 0.5385, "gamma_F18": 0.2436, "gamma_Ga68": 0.2436},
            "Beton_rendah": {"gamma_Tc99m": 0.4389, "gamma_Lu177": 0.5194, "gamma_I131": 0.4847, "gamma_F18": 0.7475, "gamma_Ga68": 0.7475},
            "Beton_tinggi": {"gamma_Tc99m": 0.3622, "gamma_Lu177": 0.4404, "gamma_I131": 0.4179, "gamma_F18": 0.8600, "gamma_Ga68": 0.8600},
            "Baja":         {"gamma_Tc99m": 0.2602, "gamma_Lu177": 28.74, "gamma_I131": 0.8742, "gamma_F18": 1.223, "gamma_Ga68": 1.223}
        }

        self.occupancy = {
            "Kantor/Resepsionis (T=1)": 1.0,
            "Koridor/R. Tunggu (T=0.2)": 0.2,
            "Toilet/Gudang (T=0.05)": 0.05,
            "Area Luar (T=0.025)": 0.025
        }

        # --- UI SETUP ---
        self.create_input_panel()
        self.create_output_panel()
        self.create_composite_shielding_panel()

    def create_input_panel(self):
        # Frame Kiri (Input)
        input_frame = ttk.LabelFrame(self.root, text="Parameter Input", padding="15")
        input_frame.place(relx=0.02, rely=0.02, relwidth=0.30, relheight=0.96)

        # 1. Pilih Isotop
        ttk.Label(input_frame, text="Pilih Isotop Sumber:").pack(anchor="w", pady=(10, 2))
        self.var_isotope = tk.StringVar()
        self.cb_isotope = ttk.Combobox(input_frame, textvariable=self.var_isotope, state="readonly")
        self.cb_isotope['values'] = list(self.isotopes.keys())
        self.cb_isotope.current(0)
        self.cb_isotope.pack(fill="x")

        # 2. Aktivitas
        ttk.Label(input_frame, text="Aktivitas Sumber (GBq):").pack(anchor="w", pady=(15, 2))
        self.entry_activity = ttk.Entry(input_frame)
        self.entry_activity.insert(0, "0.5")
        self.entry_activity.pack(fill="x")

        # 3. Jarak
        ttk.Label(input_frame, text="Jarak ke Dinding (meter):").pack(anchor="w", pady=(15, 2))
        self.entry_distance = ttk.Entry(input_frame)
        self.entry_distance.insert(0, "2.0")
        self.entry_distance.pack(fill="x")

        # 4. Beban Kerja
        ttk.Label(input_frame, text="Durasi Paparan (jam/minggu):").pack(anchor="w", pady=(15, 2))
        self.entry_workload = ttk.Entry(input_frame)
        self.entry_workload.insert(0, "40")
        self.entry_workload.pack(fill="x")

        # 5. Faktor Okupansi
        ttk.Label(input_frame, text="Tipe Ruangan Sebelah (T):").pack(anchor="w", pady=(15, 2))
        self.var_occupancy = tk.StringVar()
        self.cb_occupancy = ttk.Combobox(input_frame, textvariable=self.var_occupancy, state="readonly")
        self.cb_occupancy['values'] = list(self.occupancy.keys())
        self.cb_occupancy.current(0)
        self.cb_occupancy.pack(fill="x")

        # 6. Material Shielding (Single)
        ttk.Label(input_frame, text="Material Shielding (Single):").pack(anchor="w", pady=(15, 2))
        self.var_material = tk.StringVar()
        self.cb_material = ttk.Combobox(input_frame, textvariable=self.var_material, state="readonly")
        self.cb_material['values'] = list(self.materials_alfa.keys())
        self.cb_material.current(0)
        self.cb_material.pack(fill="x")

        # Tombol Hitung
        btn_calc = ttk.Button(input_frame, text="HITUNG SIMULASI", command=self.calculate)
        btn_calc.pack(pady=30, fill="x", ipady=5)

    def create_composite_shielding_panel(self):
        # Frame Tengah (Shielding Komposit)
        comp_frame = ttk.LabelFrame(self.root, text="Shielding Komposit (2 Material)", padding="15")
        comp_frame.place(relx=0.33, rely=0.02, relwidth=0.30, relheight=0.96)
        
        ttk.Label(comp_frame, text="Material 1 (Lapisan Luar):", font=("Arial", 10)).pack(anchor="w", pady=(10, 2))
        self.var_mat1 = tk.StringVar()
        self.cb_mat1 = ttk.Combobox(comp_frame, textvariable=self.var_mat1, state="readonly")
        self.cb_mat1['values'] = list(self.materials_alfa.keys())
        self.cb_mat1.current(0)
        self.cb_mat1.pack(fill="x")
        
        ttk.Label(comp_frame, text="Ketebalan Material 1 (mm):").pack(anchor="w", pady=(15, 2))
        self.entry_thickness1 = ttk.Entry(comp_frame)
        self.entry_thickness1.insert(0, "10")
        self.entry_thickness1.pack(fill="x")
        
        ttk.Label(comp_frame, text="\nMaterial 2 (Lapisan Dalam):", font=("Arial", 10)).pack(anchor="w", pady=(10, 2))
        self.var_mat2 = tk.StringVar()
        self.cb_mat2 = ttk.Combobox(comp_frame, textvariable=self.var_mat2, state="readonly")
        self.cb_mat2['values'] = list(self.materials_alfa.keys())
        self.cb_mat2.current(1)
        self.cb_mat2.pack(fill="x")
        
        ttk.Label(comp_frame, text="Ketebalan Material 2 (mm):").pack(anchor="w", pady=(15, 2))
        self.entry_thickness2 = ttk.Entry(comp_frame)
        self.entry_thickness2.insert(0, "50")
        self.entry_thickness2.pack(fill="x")
        
        # Radio button untuk mode perhitungan
        self.comp_mode = tk.StringVar(value="calc_transmission")
        
        ttk.Radiobutton(comp_frame, text="Hitung Transmisi Total", 
                       variable=self.comp_mode, value="calc_transmission").pack(anchor="w", pady=(20, 5))
        ttk.Radiobutton(comp_frame, text="Hitung Kebutuhan Tebal Material 2", 
                       variable=self.comp_mode, value="calc_thickness").pack(anchor="w", pady=5)
        
        # Entry untuk target transmisi (jika mode hitung ketebalan)
        ttk.Label(comp_frame, text="Target Transmisi (%):").pack(anchor="w", pady=(15, 2))
        self.entry_target_trans = ttk.Entry(comp_frame)
        self.entry_target_trans.insert(0, "1.0")
        self.entry_target_trans.pack(fill="x")
        
        btn_comp_calc = ttk.Button(comp_frame, text="HITUNG KOMPOSIT", command=self.calculate_composite)
        btn_comp_calc.pack(pady=30, fill="x", ipady=5)
        
        # Frame untuk hasil komposit
        self.comp_result_frame = ttk.LabelFrame(comp_frame, text="Hasil Shielding Komposit", padding="10")
        self.comp_result_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.lbl_comp_result = tk.Text(self.comp_result_frame, height=8, bg="#f0f0f0", 
                                       font=("Consolas", 9), width=30)
        self.lbl_comp_result.pack(fill="both", expand=True)
        self.lbl_comp_result.config(state="disabled")

    def create_output_panel(self):
        # Frame Kanan (Output & Grafik)
        output_frame = ttk.LabelFrame(self.root, text="Hasil Analisis", padding="10")
        output_frame.place(relx=0.65, rely=0.02, relwidth=0.33, relheight=0.96)

        # Area Teks Hasil
        self.lbl_result_header = ttk.Label(output_frame, text="Hasil Perhitungan:", font=("Arial", 11, "bold"))
        self.lbl_result_header.pack(anchor="w")

        self.txt_result = tk.Text(output_frame, height=8, bg="#f0f0f0", font=("Consolas", 10))
        self.txt_result.pack(fill="x", pady=6)
        self.txt_result.config(state="disabled")

        # Area Grafik Matplotlib
        self.figure = plt.Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, output_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

    def get_parameters(self, isotope_name, material_name):
        """Ambil parameter alfa, beta, dan gamma untuk kombinasi isotop dan material"""
        iso_key = isotope_name.replace("-", "")
        
        alfa_key = f"alfa_{iso_key}"
        beta_key = f"beta_{iso_key}"
        gamma_key = f"gamma_{iso_key}"
        
        alfa = self.materials_alfa[material_name].get(alfa_key, 0.1)
        beta = self.materials_beta[material_name].get(beta_key, 0.0)
        gamma = self.materials_gamma[material_name].get(gamma_key, 0.5)
        
        return alfa, beta, gamma

    def calculate_buildup_factor(self, alfa, beta, gamma, x):
        """
        Menghitung transmission factor B dari ketebalan x menggunakan inverse formula:
        x = (1/(α·γ)) · ln((B^(-γ) + β/α) / (1 + β/α))
        
        B adalah transmission factor (dose_after = B × dose_before)
        """
        try:
            # Validasi input
            if alfa <= 0 or abs(gamma) < 1e-10:
                return 1.0
            
            if x <= 0:
                return 1.0  # Tidak ada ketebalan = tidak ada atenuasi
            
            # Hitung term-term dalam formula
            exp_term = np.exp(x * alfa * gamma)
            
            # Periksa overflow
            if np.isinf(exp_term) or np.isnan(exp_term):
                # Untuk nilai sangat besar, B mendekati 0 (atenuasi sempurna)
                return 1e-10
            
            beta_alfa_ratio = beta / alfa
            
            # Hitung B^(-gamma)
            numerator_part = exp_term * (1 + beta_alfa_ratio) - beta_alfa_ratio
            
            # Validasi numerator
            if numerator_part <= 0:
                # Jika numerator negatif atau nol, kemungkinan atenuasi sangat kuat
                return 1e-10
            
            # Hitung B = (numerator_part)^(-1/gamma)
            B = numerator_part ** (-1.0 / gamma)
            
            # Validasi hasil
            if np.isnan(B) or np.isinf(B):
                return 1e-10
            
            # Clamp B ke range yang masuk akal
            B = max(1e-10, min(B, 100.0))
            
            return B
            
        except Exception as e:
            return 1.0

    def calculate_thickness_from_buildup(self, alfa, beta, gamma, B_target):
        """
        Menghitung ketebalan (x) dari transmission factor B target menggunakan formula:
        x = (1/(α·γ)) · ln((B^(-γ) + β/α) / (1 + β/α))
        
        B_target adalah transmission factor yang diinginkan (0 < B ≤ 1)
        """
        try:
            # Validasi input
            if alfa <= 0 or abs(gamma) < 1e-10:
                return 0
            
            if B_target <= 0:
                return 0
            
            if B_target >= 1.0:
                return 0  # Tidak perlu shielding
            
            beta_alfa_ratio = beta / alfa
            
            numerator = B_target**(-gamma) + beta_alfa_ratio
            denominator = 1 + beta_alfa_ratio
            
            if numerator <= 0 or denominator <= 0:
                return 0
            
            ln_term = np.log(numerator / denominator)
            
            if np.isnan(ln_term) or np.isinf(ln_term):
                return 0
            
            x = ln_term / (alfa * gamma)
            
            return max(0, x)  # Pastikan tidak negatif
            
        except Exception as e:
            return 0

    def calculate_transmission_with_buildup(self, alfa, beta, gamma, thickness_mm):
        """
        Menghitung transmission factor B dari ketebalan material
        
        Returns:
            B: transmission factor (dose setelah shielding = B × dose sebelum shielding)
        """
        thickness_cm = thickness_mm 
        
        B = self.calculate_buildup_factor(alfa, beta, gamma, thickness_mm)
        
        return B

    def calculate_transmission_composite(self, iso_name, mat1_name, thickness1, mat2_name, thickness2):
        """
        Menghitung transmisi total untuk shielding komposit
        
        FISIKA: I_final = I_0 × B1 × B2
        - Radiasi melewati Material 1: I_1 = I_0 × B1
        - Radiasi melewati Material 2: I_2 = I_1 × B2 = I_0 × B1 × B2
        """
        alfa1, beta1, gamma1 = self.get_parameters(iso_name, mat1_name)
        alfa2, beta2, gamma2 = self.get_parameters(iso_name, mat2_name)
        
        # Transmission factor masing-masing material
        B1 = self.calculate_transmission_with_buildup(alfa1, beta1, gamma1, thickness1)
        B2 = self.calculate_transmission_with_buildup(alfa2, beta2, gamma2, thickness2)
        
        # FISIKA: Transmission factor total = perkalian transmission factor masing-masing lapisan
        total_B = B1 * B2
        total_transmission_percent = total_B * 100
        
        # Hitung ketebalan equivalen timbal (Pb)
        alfa_pb, beta_pb, gamma_pb = self.get_parameters(iso_name, "Timbal (Pb)")
        
        # Gunakan formula langsung untuk mencari ketebalan Pb ekuivalen
        equivalent_pb_thickness = self.calculate_thickness_from_buildup(alfa_pb, beta_pb, gamma_pb, total_B)
        #equivalent_pb_thickness = equivalent_pb_thickness_cm 
        
        return {
            'total_transmission': total_B,
            'total_transmission_percent': total_transmission_percent,
            'trans1': B1,
            'trans2': B2,
            'B1': B1,
            'B2': B2,
            'alfa1': alfa1,
            'alfa2': alfa2,
            'equivalent_pb': equivalent_pb_thickness
        }

    def calculate_required_thickness(self, iso_name, mat1_name, thickness1, mat2_name, target_trans_percent):
        """
        Menghitung ketebalan material 2 yang dibutuhkan untuk mencapai target transmisi
        
        FISIKA:
        - Target: B_total = target_B
        - Sudah ada: B1 dari Material 1
        - Dicari: ketebalan Material 2 yang menghasilkan B2 sedemikian rupa sehingga B1 × B2 = target_B
        - Maka: B2 = target_B / B1
        """
        alfa1, beta1, gamma1 = self.get_parameters(iso_name, mat1_name)
        alfa2, beta2, gamma2 = self.get_parameters(iso_name, mat2_name)
        
        target_B = target_trans_percent / 100.0
        
        # Transmission factor material 1
        B1 = self.calculate_transmission_with_buildup(alfa1, beta1, gamma1, thickness1)
        
        # VALIDASI FISIKA 1: Apakah Material 1 sudah terlalu bagus?
        if B1 <= target_B:
            # Material 1 sudah memberikan transmisi ≤ target
            # Tidak perlu Material 2!
            return {
                'status': 'material1_sufficient',
                'B1': B1,
                'target_B': target_B,
                'message': f'Material 1 sudah cukup (B1={B1:.6f} ≤ target={target_B:.6f})'
            }
        
        # FISIKA: B_total = B1 × B2, maka B2 = B_total / B1
        required_B2 = target_B / B1
        
        # VALIDASI FISIKA 2: Apakah required_B2 masuk akal?
        # Untuk shielding normal: 0 < B2 < 1
        # Buildup bisa membuat B2 > 1, tapi jarang > 10
        if required_B2 > 10:
            return {
                'status': 'impossible',
                'B1': B1,
                'required_B2': required_B2,
                'message': f'Target tidak realistis (memerlukan B2={required_B2:.2f} > 10)'
            }
        
        # Gunakan formula langsung untuk mencari ketebalan
        thickness2 = self.calculate_thickness_from_buildup(alfa2, beta2, gamma2, required_B2)
        #thickness2 = thickness2_cm * 10  # Konversi cm ke mm
        
        # VALIDASI FISIKA 3: Apakah ketebalan terlalu besar (tidak praktis)?
        if thickness2 > 1000:  # 1 meter
            return {
                'status': 'impractical',
                'required_thickness2': thickness2,
                'B1': B1,
                'required_B2': required_B2,
                'message': f'Ketebalan terlalu besar ({thickness2:.1f} mm > 1000 mm)'
            }
        
        # Hitung B2 aktual yang dicapai (untuk verifikasi)
        B2_actual = self.calculate_transmission_with_buildup(alfa2, beta2, gamma2, thickness2)
        
        # VERIFIKASI: Apakah B1 × B2_actual ≈ target_B?
        actual_total_B = B1 * B2_actual
        error_percent = abs(actual_total_B - target_B) / target_B * 100
        
        return {
            'status': 'success',
            'required_thickness2': thickness2,
            'trans1': B1,
            'B1': B1,
            'B2': B2_actual,
            'required_B2': required_B2,
            'alfa1': alfa1,
            'alfa2': alfa2,
            'actual_trans1_percent': B1 * 100,
            'target_trans_percent': target_trans_percent,
            'actual_total_B': actual_total_B,
            'error_percent': error_percent
        }

    def calculate_composite(self):
        try:
            iso_name = self.var_isotope.get()
            mat1_name = self.var_mat1.get()
            mat2_name = self.var_mat2.get()
            
            thickness1 = float(self.entry_thickness1.get())
            thickness2 = float(self.entry_thickness2.get())
            target_trans_percent = float(self.entry_target_trans.get())
            
            mode = self.comp_mode.get()
            
            result_text = f"SHIELDING KOMPOSIT - {iso_name}\n"
            result_text += "="*40 + "\n"
            result_text += f"Material 1: {mat1_name} ({thickness1} mm)\n"
            result_text += f"Material 2: {mat2_name}\n"
            
            if mode == "calc_transmission":
                result = self.calculate_transmission_composite(iso_name, mat1_name, thickness1, 
                                                              mat2_name, thickness2)
                
                result_text += f"\n--- HASIL PERHITUNGAN ---\n"
                result_text += f"Ketebalan Material 2: {thickness2} mm\n"
                result_text += f"α {mat1_name}: {result['alfa1']:.4f} mm⁻¹\n"
                result_text += f"α {mat2_name}: {result['alfa2']:.4f} mm⁻¹\n"
                result_text += f"Transmission Factor {mat1_name} (B1): {result['B1']:.6f}\n"
                result_text += f"Transmission Factor {mat2_name} (B2): {result['B2']:.6f}\n"
                result_text += f"Transmisi {mat1_name}: {result['trans1']*100:.4f}%\n"
                result_text += f"Transmisi {mat2_name}: {result['trans2']*100:.4f}%\n"
                result_text += "-"*30 + "\n"
                result_text += f"TRANSMISI TOTAL (B1×B2): {result['total_transmission_percent']:.6f}%\n"
                result_text += f"Ketebalan Equivalen Pb: {result['equivalent_pb']:.2f} mm\n"
                
                # INTERPRETASI BERDASARKAN TRANSMISI
                result_text += "\n--- EFEKTIVITAS SHIELDING ---\n"
                if result['total_transmission_percent'] < 0.1:
                    result_text += "✓ Shielding sangat efektif (transmisi < 0.1%)\n"
                elif result['total_transmission_percent'] < 1:
                    result_text += "✓ Shielding efektif (transmisi < 1%)\n"
                elif result['total_transmission_percent'] < 5:
                    result_text += "⚠ Shielding cukup efektif (transmisi < 5%)\n"
                else:
                    result_text += "✗ Shielding kurang efektif (transmisi ≥ 5%)\n"
                
                # REKOMENDASI PRAKTIS
                result_text += "\n--- REKOMENDASI PRAKTIS ---\n"
                total_thickness = thickness1 + thickness2
                
                if total_thickness > 200:
                    result_text += "⚠ Total ketebalan sangat besar ({:.1f} mm)\n".format(total_thickness)
                    result_text += "  Pertimbangkan material dengan densitas lebih tinggi\n"
                elif total_thickness > 100:
                    result_text += "○ Total ketebalan cukup besar ({:.1f} mm)\n".format(total_thickness)
                    result_text += "  Masih dalam batas praktis untuk konstruksi\n"
                else:
                    result_text += "✓ Total ketebalan praktis ({:.1f} mm)\n".format(total_thickness)
                    result_text += "  Desain mudah diimplementasikan\n"
                    
            else:  # calc_thickness mode
                result = self.calculate_required_thickness(iso_name, mat1_name, thickness1, 
                                                          mat2_name, target_trans_percent)
                
                # Cek status hasil
                if result['status'] == 'material1_sufficient':
                    result_text += "\n✓ MATERIAL 1 SUDAH CUKUP!\n"
                    result_text += f"Transmission Factor Material 1: {result['B1']:.6f}\n"
                    result_text += f"Transmisi Material 1: {result['B1']*100:.4f}%\n"
                    result_text += f"Target Transmisi: {target_trans_percent}%\n"
                    result_text += "-"*30 + "\n"
                    result_text += "Material 1 sudah memberikan transmisi ≤ target.\n"
                    result_text += "Tidak perlu Material 2!\n"
                    
                    # Interpretasi
                    result_text += "\n--- EFEKTIVITAS SHIELDING ---\n"
                    trans1_percent = result['B1'] * 100
                    if trans1_percent < 0.1:
                        result_text += "✓ Material 1 sangat efektif (transmisi < 0.1%)\n"
                    elif trans1_percent < 1:
                        result_text += "✓ Material 1 efektif (transmisi < 1%)\n"
                    elif trans1_percent < 5:
                        result_text += "⚠ Material 1 cukup efektif (transmisi < 5%)\n"
                    
                elif result['status'] == 'impossible':
                    result_text += "\n❌ TARGET TIDAK REALISTIS!\n"
                    result_text += f"Transmission Factor Material 1: {result['B1']:.6f}\n"
                    result_text += f"Required B2: {result['required_B2']:.2f}\n"
                    result_text += f"Target: {target_trans_percent}%\n"
                    result_text += "-"*30 + "\n"
                    result_text += result['message'] + "\n"
                    result_text += "\nSaran: Gunakan material dengan atenuasi lebih kuat\n"
                    result_text += "atau naikkan target transmisi.\n"
                    
                elif result['status'] == 'impractical':
                    result_text += "\n⚠ KETEBALAN TIDAK PRAKTIS!\n"
                    result_text += f"Ketebalan Material 2 dibutuhkan: {result['required_thickness2']:.1f} mm\n"
                    result_text += f"Transmission Factor Material 1: {result['B1']:.6f}\n"
                    result_text += f"Required B2: {result['required_B2']:.6f}\n"
                    result_text += "-"*30 + "\n"
                    result_text += "Ketebalan terlalu besar untuk konstruksi praktis.\n"
                    result_text += "\nSaran: Pilih material dengan densitas lebih tinggi.\n"
                    
                else:  # success
                    result_text += f"\n--- HASIL PERHITUNGAN ---\n"
                    result_text += f"Target Transmisi: {target_trans_percent}%\n"
                    result_text += f"α {mat1_name}: {result['alfa1']:.4f} mm⁻¹\n"
                    result_text += f"α {mat2_name}: {result['alfa2']:.4f} mm⁻¹\n"
                    result_text += f"Transmission Factor {mat1_name} (B1): {result['B1']:.6f}\n"
                    result_text += f"Transmission Factor {mat2_name} (B2): {result['B2']:.6f}\n"
                    result_text += f"Transmisi {mat1_name}: {result['actual_trans1_percent']:.4f}%\n"
                    result_text += f"Required B2 (teoritis): {result['required_B2']:.6f}\n"
                    result_text += "-"*30 + "\n"
                    result_text += f"KETEBALAN {mat2_name} DIBUTUHKAN: {result['required_thickness2']:.2f} mm\n"
                    
                    total_thickness = thickness1 + result['required_thickness2']
                    result_text += f"Total Ketebalan: {total_thickness:.2f} mm\n"
                    
                    # Transmisi total yang dicapai (verifikasi)
                    result_text += f"\n--- VERIFIKASI ---\n"
                    result_text += f"Transmisi total aktual: {result['actual_total_B']*100:.6f}%\n"
                    result_text += f"Error dari target: {result['error_percent']:.2f}%\n"
                    
                    # INTERPRETASI BERDASARKAN TRANSMISI
                    result_text += "\n--- EFEKTIVITAS SHIELDING ---\n"
                    total_trans_percent = result['actual_total_B'] * 100
                    if total_trans_percent < 0.1:
                        result_text += "✓ Shielding sangat efektif (transmisi < 0.1%)\n"
                    elif total_trans_percent < 1:
                        result_text += "✓ Shielding efektif (transmisi < 1%)\n"
                    elif total_trans_percent < 5:
                        result_text += "⚠ Shielding cukup efektif (transmisi < 5%)\n"
                    else:
                        result_text += "✗ Shielding kurang efektif (transmisi ≥ 5%)\n"
                    
                    # REKOMENDASI PRAKTIS
                    result_text += "\n--- REKOMENDASI PRAKTIS ---\n"
                    if result['required_thickness2'] > 200:
                        result_text += "✗ Material 2 terlalu tebal ({:.1f} mm)\n".format(result['required_thickness2'])
                        result_text += "  Pertimbangkan material dengan densitas lebih tinggi\n"
                    elif result['required_thickness2'] > 100:
                        result_text += "⚠ Material 2 cukup tebal ({:.1f} mm)\n".format(result['required_thickness2'])
                        result_text += "  Masih dapat diimplementasikan dengan konstruksi khusus\n"
                    elif result['required_thickness2'] > 50:
                        result_text += "○ Material 2 sedang ({:.1f} mm)\n".format(result['required_thickness2'])
                        result_text += "  Desain praktis dan mudah dikonstruksi\n"
                    elif result['required_thickness2'] > 10:
                        result_text += "✓ Material 2 tipis ({:.1f} mm)\n".format(result['required_thickness2'])
                        result_text += "  Desain optimal dan ekonomis\n"
                    else:
                        result_text += "✓ Material 2 sangat tipis ({:.1f} mm)\n".format(result['required_thickness2'])
                        result_text += "  Desain sangat optimal\n"
                    
                    # Informasi total ketebalan
                    result_text += f"\n○ Total ketebalan: {total_thickness:.1f} mm\n"
                    if total_thickness > 200:
                        result_text += "  Pertimbangkan redesign dengan material lebih efektif\n"
                    else:
                        result_text += "  Total ketebalan dalam batas praktis\n"
            
            self.lbl_comp_result.config(state="normal")
            self.lbl_comp_result.delete(1.0, tk.END)
            self.lbl_comp_result.insert(tk.END, result_text)
            self.lbl_comp_result.config(state="disabled")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Pastikan semua angka valid!\nDetails: {e}")

    def calculate(self):
        try:
            # 1. Ambil Data
            iso_name = self.var_isotope.get()
            mat_name = self.var_material.get()
            occ_name = self.var_occupancy.get()
            
            activity = float(self.entry_activity.get())
            dist = float(self.entry_distance.get())
            workload = float(self.entry_workload.get())
            
            # Validasi input negatif/nol
            if dist <= 0: raise ValueError("Jarak harus > 0")

            # 2. Parameter Fisika
            gamma_coef = self.isotopes[iso_name]["gamma_coef"]
            alfa, beta, gamma = self.get_parameters(iso_name, mat_name)
            occupancy_factor = self.occupancy[occ_name]
            limit_dose_weekly = 0.02  # mSv/minggu (Batas aman publik)

            # 3. Perhitungan
            # Laju Dosis di titik tinjau (mSv/h)
            dose_rate_hourly = (gamma_coef * activity) / (dist ** 2)
            
            # Dosis Mingguan Potensial (Tanpa Shielding)
            potential_weekly_dose = dose_rate_hourly * workload * occupancy_factor
            
            # Hitung Tebal Shielding
            req_thickness = 0
            status_msg = "AMAN (Tidak butuh shielding)"
            transmission_factor = 1.0
            dose_after_shielding = potential_weekly_dose
            
            if potential_weekly_dose > limit_dose_weekly:
                # Target transmission factor yang dibutuhkan
                target_B = limit_dose_weekly / potential_weekly_dose
                
                # Gunakan formula langsung untuk mencari ketebalan
                req_thickness = self.calculate_thickness_from_buildup(alfa, beta, gamma, target_B)
                #req_thickness = req_thickness_cm * 10  # Konversi cm ke mm
                
                # Hitung transmission factor aktual yang dicapai
                transmission_factor = self.calculate_transmission_with_buildup(alfa, beta, gamma, req_thickness)
                
                # Hitung dose setelah shielding
                dose_after_shielding = transmission_factor * potential_weekly_dose
                status_msg = f"PERLU SHIELDING: {req_thickness:.2f} mm"

            # 4. Tampilkan Teks Hasil
            result_text = (
                f"Isotop: {iso_name} | Material: {mat_name}\n"
                f"Laju Dosis (jarak {dist}m): {dose_rate_hourly:.4f} mSv/h\n"
                f"Dosis Mingguan Potensial: {potential_weekly_dose:.4f} mSv\n"
                f"Dosis Setelah Shielding: {dose_after_shielding:.4f} mSv\n"
                f"Batas Aman: {limit_dose_weekly} mSv/minggu\n"
                f"α: {alfa:.4f} mm⁻¹ | β: {beta:.4f} | γ: {gamma:.4f}\n"
                f"Transmission Factor (B): {transmission_factor:.6f}\n"
                f"-" * 40 + "\n"
                f"STATUS: {status_msg}"
            )
            
            self.txt_result.config(state="normal")
            self.txt_result.delete(1.0, tk.END)
            self.txt_result.insert(tk.END, result_text)
            self.txt_result.config(state="disabled")

            # 5. Update Grafik
            self.plot_graph(req_thickness, alfa, beta, gamma, potential_weekly_dose, limit_dose_weekly, mat_name)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Pastikan semua angka valid!\nDetails: {e}")

    def plot_graph(self, req_thickness, alfa, beta, gamma, potential_dose, limit, mat_name):
        self.ax.clear()
        
        # Tentukan rentang sumbu X (Ketebalan)
        max_x = req_thickness * 1.5 if req_thickness > 0 else 100
        x = np.linspace(0, max_x, 100)
        
        # Hitung kurva atenuasi dengan transmission factor
        y = []
        for thickness in x:
            B = self.calculate_transmission_with_buildup(alfa, beta, gamma, thickness)
            dose = B * potential_dose  # dose setelah = B × dose sebelum
            y.append(dose)
        
        # Plotting
        self.ax.plot(x, y, label='Penurunan Dosis', color='#007acc', linewidth=2)
        self.ax.axhline(y=limit, color='#d62728', linestyle='--', label=f'Batas ({limit} mSv)')
        
        # Jika shielding dibutuhkan, beri titik penanda
        if req_thickness > 0:
            self.ax.plot(req_thickness, limit, 'o', color='green', markersize=8)
            self.ax.annotate(f'{req_thickness:.1f} mm', 
                             xy=(req_thickness, limit), 
                             xytext=(10, 20), textcoords='offset points',
                             arrowprops=dict(facecolor='black', arrowstyle='->'))

        self.ax.set_title(f"Kurva Atenuasi {mat_name}")
        self.ax.set_xlabel("Ketebalan (mm)")
        self.ax.set_ylabel("Dosis Mingguan (mSv)")
        self.ax.grid(True, which='both', linestyle='--', alpha=0.5)
        self.ax.legend()
        
        # Refresh canvas
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    # Setting tema agar terlihat tidak terlalu "jadul"
    try:
        style = ttk.Style()
        style.theme_use('clam') 
    except:
        pass
        
    app = ShieldingCalcGUI(root)
    root.mainloop()