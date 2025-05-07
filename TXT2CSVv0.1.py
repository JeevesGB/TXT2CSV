import os
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

def get_input_for_headers(headers):
    data = {}
    for header in headers:
        value = input(f"Enter {header} (press Enter to skip): ")
        data[header] = value if value else ""
    return data
#       #        #      #
#       TXT 2 CSV       #
#           BY          #
#          JEJ          #
#      #         #      #

headers = {
    "Brake": ["CarId", "Price", "Stage", "BrakingPower", "FrontBrakesUnknown", "RearBrakesUnknown"],
    "BrakeController": ["CarId", "Price", "Stage", "MaxFrontBias", "Unknown", "Unknown2", "DefaultBias", "MaxRearBias", "Unknown3", "Unknown4"],
    "Car": ["CarId", "Brake", "BrakeController", "Steer", "Chassis", "Lightweight", "RacingModify", "Engine", "PortPolish", "EngineBalance", "Displacement", "Computer", "NATune", "TurbineKit", "Drivetrain", "Flywheel", "Clutch", "PropellerShaft", "LSD", "Gear", "Suspension", "Intercooler", "Muffler", "TiresFront", "TiresRear", "ActiveStabilityControl", "TractionControlSystem", "RimsCode3", "ManufacturerID", "HasAllTiresBought", "Unknown", "Price"],
    "Chassis": ["CarId", "FrontWeightDistribution", "Unknown2", "FrontGrip", "RearGrip", "Length", "Height", "Wheelbase", "Weight", "TurningResistance", "PitchResistance", "RollResistance", "Unknown8"],
    "Clutch": ["CarId", "Price", "Stage", "RPMDropRate", "InertiaDisengaged", "InertiaEngaged", "InertialWeight", "InertiaBraking", "Unknown1", "Unknown2"],
    "Computer": ["CarId", "Price", "Stage", "PowerbandScaling", "RPMIncrease", "PowerMultiplier"],
    "Displacement": ["CarId", "Price", "Stage", "PowerbandScaling", "RPMIncrease", "PowerMultiplier"],
    "Drivetrain": ["CarId", "Unknown", "Unknown2", "Unknown3", "Unknown4", "DrivetrainType", "AWDBehaviour", "DefaultClutchRPMDropRate", "DefaultClutchInertiaEngaged", "DefaultClutchInertialWeight", "DefaultClutchInertiaDisengaged", "FrontDriveInertia", "RearDriveInertia"],
    "EnemyCars": ["CarId", "Brake", "BrakeController", "Steer", "Chassis", "Lightweight", "RacingModify", "Engine", "PortPolish", "EngineBalance", "Displacement", "Computer", "NATune", "TurbineKit", "Drivetrain", "Flywheel", "Clutch", "Propshaft", "LSD", "Gear", "Suspension", "Intercooler", "Muffler", "TiresFront", "TiresRear", "ActiveStabilityControl", "TractionControlSystem", "RimsCode3", "FinalDriveRatio", "GearAutoSetting", "LSDInitialFront", "LSDAccelFront", "LSDDecelFront", "LSDInitialRearAYCLevel", "LSDAccelRear", "LSDDecelRear", "DownforceFront", "DownforceRear", "CamberFront", "CamberRear", "ToeFront", "ToeRear", "RideHeightFront", "RideHeightRear", "SpringRateFront", "SpringRateRear", "DamperBoundFront1", "DamperBoundFront2", "DamperReboundFront1", "DamperReboundFront2", "DamperBoundRear1", "DamperBoundRear2", "DamperReboundRear1", "DamperReboundRear2", "StabiliserFront", "StabiliserRear", "ASMLevel", "TCSLevel", "Unknown3", "Unknown4", "PowerMultiplier", "OpponentId"],
    "Engine": ["CarId", "LayoutName", "ValvetrainName", "Aspiration", "SoundFile", "TorqueCurve1", "TorqueCurve2", "TorqueCurve3", "TorqueCurve4", "TorqueCurve5", "TorqueCurve6", "TorqueCurve7", "TorqueCurve8", "TorqueCurve9", "TorqueCurve10", "TorqueCurve11", "TorqueCurve12", "TorqueCurve13", "TorqueCurve14", "TorqueCurve15", "TorqueCurve16", "Displacement", "DisplayedPower", "MaxPowerRPM", "DisplayedTorque", "MaxTorqueRPMName", "PowerMultiplier", "ClutchReleaseRPM", "IdleRPM", "MaxRPM", "RedlineRPM", "TorqueCurveRPM1", "TorqueCurveRPM2", "TorqueCurveRPM3", "TorqueCurveRPM4", "TorqueCurveRPM5", "TorqueCurveRPM6", "TorqueCurveRPM7", "TorqueCurveRPM8", "TorqueCurveRPM9", "TorqueCurveRPM10", "TorqueCurveRPM11", "TorqueCurveRPM12", "TorqueCurveRPM13", "TorqueCurveRPM14", "TorqueCurveRPM15", "TorqueCurveRPM16", "TorqueCurvePoints"],
    "EngineBalance": ["CarId", "Price", "Stage", "PowerbandScaling", "RPMIncrease", "PowerMultiplier"],
    "Event": ["EventName", "TrackName", "Opponent1", "Opponent2", "Opponent3", "Opponent4", "Opponent5", "Opponent6", "Opponent7", "Opponent8", "Opponent9", "Opponent10", "Opponent11", "Opponent12", "Opponent13", "Opponent14", "Opponent15", "Opponent16", "RollingStartSpeed", "Laps", "AutoDrive", "Licence", "AIFrontGripRWD", "AIFrontGripFWD", "AIFrontGrip4WD", "AIFrontGripSpecial4WD", "AIRearGripRWD", "AIRearGripFWD", "AIRearGrip4WD", "AIRearGripSpecial4WD", "AIAccelerationRWD", "AIAccelerationFWD", "AIAcceleration4WD", "AIAccelerationSpecial4WD", "AIThrottleLiftReductionRWD", "AIThrottleLiftReductionFWD", "AIThrottleLiftReduction4WD", "AIThrottleLiftReductionSpecial4WD", "AIRubberBandMultiplier", "AIRubberBandUnknown1", "AIRubberBandScaledPerCar", "AIRubberBandLeadingSlowdownPercentage", "AIRubberBandLeadingScalingDistance", "AIRubberBandTrailingSpeedupPercentage", "AIRubberBandTrailingScalingDistance", "TireWearOrangeDurationMultiplier", "TireWearOrangeGripLoss", "TireWearUnknown", "TireWearBlueDurationMultiplier", "TireWearBlueGripLoss", "TireWearGreenDurationMultiplier", "TireWearGreenGripLoss", "Unknown1", "Unknown2", "Unknown3", "Unknown4", "IsRally", "EligibleCarsRestriction", "DrivetrainRestriction", "PrizeMoney1st", "PrizeMoney2nd", "PrizeMoney3rd", "PrizeMoney4th", "PrizeMoney5th", "PrizeMoney6th", "PrizeCars", "TrackBannerPool", "PSRestriction", "SeriesChampBonus", "CarRestrictionFlags"],
    "Flywheel": ["CarId", "Price", "Stage", "RPMDropRate", "ShiftDelay", "InertialWeight"],
    "Gear": ["CarId", "Price", "Stage", "NumberOfGears", "ReverseGearRatio", "FirstGearRatio", "SecondGearRatio", "ThirdGearRatio", "FourthGearRatio", "FifthGearRatio", "SixthGearRatio", "SeventhGearRatio", "DefaultFinalDriveRatio", "MaxFinalDriveRatio", "MinFinalDriveRatio", "AllowIndividualRatioAdjustments", "DefaultAutoSetting", "MinAutoSetting", "MaxAutoSetting"],
    "Intercooler": ["CarId", "Price", "Stage", "PowerbandScaling", "RPMIncrease", "PowerMultiplier"],
    "Lightweight": ["CarId", "Price", "Weight", "Unknown", "Stage"],
    "LSD": ["CarId", "Price", "Stage", "Unknown", "Unknown2", "Unknown3", "FrontUnknown", "DefaultInitialFront", "MinInitialFront", "MaxInitialFront", "DefaultAccelFront", "MinAccelFront", "MaxAccelFront", "DefaultDecelFront", "MinDecelFront", "MaxDecelFront", "RearUnknown", "DefaultInitialRear", "MinInitialRear", "MaxInitialRear", "DefaultAccelRear", "MinAccelRear", "MaxAccelRear", "DefaultDecelRear", "MinDecelRear", "MaxDecelRear"],
    "Muffler": ["CarId", "Price", "Stage", "PowerbandScaling", "RPMIncrease", "PowerMultiplier"],
    "NATune": ["CarId", "Price", "Stage", "PowerbandRPMIncrease", "RPMIncrease", "PowerMultiplier"],
    "PortPolish": ["CarId", "Price", "Stage", "PowerbandScaling", "RPMIncrease", "PowerMultiplier"],
    "PropellerShaft": ["CarId", "Price", "Stage", "RPMDropRate", "Inertia", "Inertia2"],
    "RacingModify": ["CarId", "Price", "BodyId", "Weight", "BodyRollAmount", "Stage", "Drag", "FrontDownforceMinimum", "FrontDownforceMaximum", "FrontDownforceDefault", "RearDownforceMinimum", "RearDownforceMaximum", "RearDownforceDefault", "Unknown3", "Unknown4", "Unknown5", "Unknown6", "Width"],
    "Regulations": ["EligibleCarIds"],
    "Steer": ["CarId", "Price", "Stage", "Unknown1", "Angle1Speed", "Angle2Speed", "Angle3Speed", "Angle4Speed", "Angle5Speed", "Angle6Speed", "Angle1", "Angle2", "Angle3", "Angle4", "Angle5", "Angle6", "MaxSteeringAngle", "Unknown2"],
    "Strings": ["CarID", "NameFirstPart", "NameSecondPart", "Year"],
    "Suspension": ["CarId", "Price", "Stage", "MinCamberFront", "MaxCamberFront", "DefaultCamberFront", "MinCamberRear", "MaxCamberRear", "DefaultCamberRear", "MinToeFront", "MaxToeFront", "MinToeRear", "MaxToeRear", "MinHeightFront", "MaxHeightFront", "DefaultHeightFront", "MinHeightRear", "MaxHeightRear", "DefaultHeightRear", "DampingFront", "DampingRear", "TravelFront", "TravelRear", "MinSpringRateFront", "MaxSpringRateFront", "DefaultSpringRateFront", "MinSpringRateRear", "MaxSpringRateRear", "DefaultSpringRateRear", "SpringFrequencyFront", "SpringFrequencyRear", "Unknown7", "Unknown8", "MaxDamperBoundFront", "Unknown9", "Unknown10", "DefaultDamperBoundFront", "Unknown11", "Unknown12", "Unknown13", "MaxDamperReboundFront", "Unknown14", "Unknown15", "DefaultDamperReboundFront", "Unknown16", "Unknown17", "Unknown18", "MaxDamperBoundRear", "Unknown19", "Unknown20", "DefaultDamperBoundRear", "Unknown21", "Unknown22", "Unknown23", "MaxDamperReboundRear", "Unknown24", "Unknown25", "DefaultDamperReboundRear", "Unknown26", "Unknown27", "Unknown28", "MaxStabiliserFront", "Unknown29", "Unknown30", "DefaultStabiliserFront", "MaxStabiliserRear", "Unknown31", "Unknown32", "DefaultStabiliserRear", "Unknown33"],
    "TireSize": ["DiameterInches", "WidthMM", "Profile"],
    "TiresFront": ["CarId", "Price", "Stage", "SteeringReaction1", "WheelSize", "SteeringReaction2", "TireCompound", "TireForceVolMaybe", "SlipMultiplier", "GripMultiplier"],
    "TiresRear": ["CarId", "Price", "Stage", "SteeringReaction1", "WheelSize", "SteeringReaction2", "TireCompound", "TireForceVolMaybe", "SlipMultiplier", "GripMultiplier"],
    "TurbineKit": ["CarId", "Price", "Stage", "BoostGaugeLimit", "LowRPMBoost", "HighRPMBoost", "SpoolRate", "Unknown1", "Unknown2", "Unknown3", "RPMIncrease", "RedlineIncrease", "HighRPMPowerMultiplier", "LowRPMPowerMultiplier"],
    "Wheel": ["WheelId", "StageMaybe", "Unknown", "Unknown2", "Unknown3"]
}


class CSVGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TXT-2-CSV")
        self.root.geometry("350x450")


        tk.Label(root, text="Select Tab:").pack(pady=5)
        self.tab_var = tk.StringVar()
        self.tab_dropdown = ttk.Combobox(root, textvariable=self.tab_var, values=list(headers.keys()))
        self.tab_dropdown.pack(pady=5)
        self.tab_dropdown.bind("<<ComboboxSelected>>", self.update_input_fields)


        self.input_frame = tk.Frame(root)
        self.input_frame.pack(fill="both", expand=True, padx=5, pady=5)


        self.canvas = tk.Canvas(self.input_frame)
        self.scrollbar = tk.Scrollbar(self.input_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")


        self.entries = {}


        tk.Button(root, text="Generate CSV", command=self.on_generate_csv).pack(pady=10)
        tk.Button(root, text="Import CSV", command=self.import_csv).pack(pady=5)

        self.status_label = tk.Label(root, text="", wraplength=500)
        self.status_label.pack(pady=5)

    from tkinter import filedialog

    def import_csv(self):
        selected_tab = self.tab_var.get()
        if not selected_tab:
            messagebox.showwarning("No Tab Selected", "Please select a tab before importing.")
            return

        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return  # Cancelled

        try:
            with open(filepath, newline='') as file:
                reader = csv.reader(file)
                rows = list(reader)
                if len(rows) < 2:
                    messagebox.showerror("Invalid CSV", "CSV must have at least two rows (header + data).")
                    return

                # Use second row as data (first row is header)
                data_row = rows[1]
                expected_headers = headers[selected_tab]

                for idx, header in enumerate(expected_headers):
                    if idx < len(data_row):
                        entry_widget = self.entries.get(header)
                        if entry_widget:
                            entry_widget.delete(0, tk.END)
                            value = data_row[idx]
                            #value = value.replace(".csv", "")
                            #value = os.path.basename(value)

                            entry_widget.insert(0, value)

                self.status_label.config(text=f"Data loaded from '{filepath}'")

        except Exception as e:
            messagebox.showerror("Import Failed", f"Failed to import CSV: {e}")

    def update_input_fields(self, event=None):

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()


        selected_tab = self.tab_var.get()
        if not selected_tab:
            return


        for header in headers[selected_tab]:
            frame = tk.Frame(self.scrollable_frame)
            frame.pack(fill="x", expand=True, pady=2)

            tk.Label(frame, text=header, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(frame, width=40)  # Increase width as needed
            entry.pack(side="left", padx=5)

            self.entries[header] = entry

    def generate_csv(self, selected_tab, expected_headers, data):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV As"
        )

        if not file_path:
            return False, "Save operation cancelled."

        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(expected_headers)
                writer.writerow([data.get(header, "") for header in expected_headers])
            return True, f"CSV saved as '{file_path}'"
        except Exception as e:
            return False, f"Error saving CSV: {e}"

    def on_generate_csv(self):
        selected_tab = self.tab_var.get()
        if not selected_tab:
            messagebox.showwarning("No Tab Selected", "Please select a tab.")
            return

        data = {header: entry.get() for header, entry in self.entries.items()}
        success, message = self.generate_csv(selected_tab, headers[selected_tab], data)
        self.status_label.config(text=message)


if __name__ == "__main__":
    root = tk.Tk()
    app = CSVGeneratorApp(root)
    root.mainloop()