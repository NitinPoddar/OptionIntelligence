import pandas as pd

def compile_user_input(user_input):
    lines = user_input.strip().split("\n")
    output = []
    Counter = 1
    instrument_List = []  # Define instrument_List as needed
    MarketConnection = None  # Define MarketConnection as needed
    AngelMarketConnect = None  # Define AngelMarketConnect as needed
    
    for line in lines:
        if line.startswith("Create"):
            # Parse LegName, Script, Exchange from "Create Leg="A" Script="BANKNIFTY" Exchange="NSE"
            parts = line.split(" ")
            LegName = None
            Script = None
            Exchange = None
            
            for part in parts:
                if part.startswith("Leg="):
                    LegName = part.split("=")[1].strip('"')
                elif part.startswith("Script="):
                    Script = part.split("=")[1].strip('"')
                elif part.startswith("Exchange="):
                    Exchange = part.split("=")[1].strip('"')
            
            if LegName is None or Script is None or Exchange is None:
                print("Error: LegName, Script, or Exchange missing in Create statement.")
                continue  # Skip this line if essential details are missing
            
        elif line.startswith("Temp"):
            # Handle temporary calculations or executions if needed
            try:
                # Parse the temporary line and execute
                parts = line.split("=")
                temp_name = parts[0].strip()
                temp_call = parts[1].strip()

                # Adjust the function call to include AngelMarketConnect and instrument_List
                if temp_call.startswith("getGeeks"):
                    temp_call = temp_call.replace("getGeeks", "getGeeks(AngelMarketConnect, ")
                    temp_call = temp_call.rstrip()[:-1] + ', instrumentlist=instrument_List)'

                exec(f"{temp_name}={temp_call}", globals())
            except Exception as e:
                print(f"Error executing temporary line: {line}. Error: {str(e)}")
        
        else:
            # Parse details for each Leg
            details = {'LegName': LegName, 'Script': Script, 'Exchange': Exchange}
            
            # Extract details from the line
            parts = line.split(",")
            for part in parts:
                key_value = part.split("=")
                if len(key_value) < 2:
                    print(f"Skipping invalid line: {line}")
                    continue
                
                key = key_value[0].strip()
                value = key_value[1].strip('" ')
                
                details[key] = value
            
            # Validate mandatory fields
            if 'Script' not in details or 'LegName' not in details or 'Exchange' not in details:
                print("Error: Missing Script, LegName, or Exchange in details.")
                continue  # Skip this line if essential details are missing
            
            # Generate LegDetails function call
            LegDetails_call = f"LegDetails('{details['Script']}', instrument_List, '{details['LegName']}', '{details['Exchange']}', AngelMarketConnect)"
            
            # Generate Option function call
            option_params = {
                'OrderSide': f"'{details.get('OrderSide', '')}'",
                'LimitPrice': float(details.get('LimitPrice', 0)),
                'StrikePrice': f"'{details.get('StrikePrice', 0)}'",  # Assuming it's a number
                'delta': f"Temp3",  # Assuming Temp3 is a variable calculated earlier
                'vega': float(details.get('Vega', 0)),
                'gamma': float(details.get('Gamma', 0)),
                'Expiry': f"'{details.get('Expiry', '')}'",
                'orderType': f"'{details.get('orderType', '')}'",
                'productType': f"'{details.get('productType', '')}'",
                'instrumentlist': 'instrument_List',  # Assuming instrument_List is defined elsewhere
                'Sequence': float(details.get('Sequence', 0)),
                'Steps': float(details.get('Steps', 0)),
                'Quantity': float(details.get('Quantity', 0)),
                'OptionType': f"'{details.get('OptionType', '')}'",
                'timeInForce': f"'{details.get('timeInForce', '')}'"
            }
            
            Option_call = f"Option({LegDetails_call}, MarketConnection, AngelMarketConnect, {', '.join(f'{k}={v}' for k, v in option_params.items())})"
            Leg4_call = f"{LegDetails_call}={Option_call}"
            
            try:
                # Output Python executed code
                print(f"python executed code is :{Leg4_call}")
                
                # Optionally evaluate the call and process further if needed
                # Leg = eval(Option_call)
                # Leg['Counter'] = Counter
                # output.append(Leg)
                Counter += 1
            except Exception as e:
                print(f"Error generating Leg DataFrame: {str(e)}")
    
    # Concatenate all Leg dataframes if needed
    # if output:
    #     result = pd.concat(output, axis=0)
    # else:
    #     result = pd.DataFrame()  # Empty DataFrame if no valid data
    
    # return result

# Example usage:
