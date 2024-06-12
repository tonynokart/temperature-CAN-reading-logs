import can 
import time
import os
import csv
# run this command in terminal: 

# sudo ip link set can0 up type can bitrate 1000000
# sudo ip link set can0 down
# canplayer vcan0=can0 -v -I candump-2024-06-09_214909.log


# initialize arrays
temp_min        = [None] * 8
temp_max        = [None] * 8
temp_avg        = [None] * 8
thermistor_temp = [[None] * 20 for i in range(6)] 

table = [None] * 21

def main():

    start_seconds = time.time()
    local_time = time.ctime(start_seconds)

    try: 
        with can.interface.Bus(channel='vcan0', bustype='socketcan') as  bus:
            
            show_table()
            while(True):
                seconds = time.time()
                difference = seconds - start_seconds
               
                message = bus.recv(timeout=1.0)

                if message is not None:
                    print("received")
                    if difference < 20:
                        decode_message(message)
                        writeToCSV(difference, local_time)
                    else:
                        show_table()
                        start_seconds = time.time()
                        local_time = time.ctime(start_seconds)
                        decode_message(message)
                        writeToCSV(difference,local_time)
                        show_table()
                else:
                    print("no message")
         
    except Exception as e: 
        print(e)

def decode_message(message):
    can_id = hex(message.arbitration_id)
    
    message_data = [byte for byte in message.data]   
        
    unpack_bytearray(message_data, can_id,message.timestamp)

def unpack_bytearray(message_data, can_id, message_time):
       
    binary_data = to_bits(message_data)

    match can_id:
        case "0x100"|"0x101"|"0x102"|"0x103"|"0x104"|"0x105"|"0x106"|"0x107":
            segment_number = int(can_id, 16) - 256

            
            

        # Avg temp + SOC min/avg/max + CELL TEMP 0-1
        case "0x700"|"0x701"|"0x702"|"0x703"|"0x704"|"0x705"|"0x706"|"0x707": # WORKING
            segment_number = int(can_id, 16) - 1792
            
            temp_avg[segment_number]            = int(get_next_bits(binary_data ,10 ,7),2)
            # from bit 17 to 47 there is SoC min max avg (10 bits each)
            thermistor_temp[segment_number][0]  = int(get_next_bits(binary_data ,47 ,7),2)
            thermistor_temp[segment_number][1]  = int(get_next_bits(binary_data ,54 ,7),2)


        # CELL TEMP 2-10
        case "0x710"|"0x711"|"0x712"|"0x713"|"0x714"|"0x715"|"0x716"|"0x717": # WORKING
            segment_number = int(can_id, 16) - 1808
            
            thermistor_temp[segment_number][2] = int(get_next_bits(binary_data ,0, 7),2)
            thermistor_temp[segment_number][3]  = int(get_next_bits(binary_data ,7, 7),2)
            thermistor_temp[segment_number][4]  = int(get_next_bits(binary_data ,14, 7),2)
            thermistor_temp[segment_number][5]  = int(get_next_bits(binary_data ,21, 7),2)
            thermistor_temp[segment_number][6]  = int(get_next_bits(binary_data ,28, 7),2)
            thermistor_temp[segment_number][7]  = int(get_next_bits(binary_data ,35, 7),2)
            thermistor_temp[segment_number][8]  = int(get_next_bits(binary_data ,42, 7),2)
            thermistor_temp[segment_number][9]  = int(get_next_bits(binary_data ,49, 7),2)
            thermistor_temp[segment_number][10]  = int(get_next_bits(binary_data ,56, 7),2)

        # CELL TEMP 11-19
        case "0x720"|"0x721"|"0x722"|"0x723"|"0x724"|"0x725"|"0x726"|"0x727": # WORKING
            segment_number = int(can_id, 16) - 1824
            thermistor_temp[segment_number][11]  = int(get_next_bits(binary_data , 0, 7),2)
            thermistor_temp[segment_number][12]  = int(get_next_bits(binary_data , 7, 7),2)
            thermistor_temp[segment_number][13]  = int(get_next_bits(binary_data , 14, 7),2)
            thermistor_temp[segment_number][14]  = int(get_next_bits(binary_data , 21, 7),2)
            thermistor_temp[segment_number][15]  = int(get_next_bits(binary_data , 28, 7),2)
            thermistor_temp[segment_number][16]  = int(get_next_bits(binary_data , 35, 7),2)
            thermistor_temp[segment_number][17]  = int(get_next_bits(binary_data , 42, 7),2)
            thermistor_temp[segment_number][18]  = int(get_next_bits(binary_data , 49, 7),2)
            thermistor_temp[segment_number][19]  = int(get_next_bits(binary_data , 56, 7),2)
    
def get_next_bits(binary_string, start_bit, number_of_bits):
    message = ""
    for i in range(start_bit, start_bit + number_of_bits):
        if i >= len(binary_string):
            break
        message += binary_string[i]
    print(message)
    return message  

def to_bits(data):
    binary = ""
    for i in range(len(data)):
        i = len(data) - i - 1
        binary += bin(data[i])[2:].zfill(8)+ ""
    return binary

def writeToCSV(difference, DATE_time):
    title = "temp_"+str(DATE_time)+".csv"
    with open(title, "a", newline="") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, delimiter=" ")
        
        i = 0
        j = 0
        writer.writerow("Time,Thermistor Temp,min,avg,max,0,1,2,3,4,5")
        table[i] = "Time,Thermistor Temp,avg,0,1,2,3,4,5"
        for i in range(len(thermistor_temp[i])):
            
            full_row = str(difference)+","+"["+str(i)+"]"+","+str(temp_avg[j])
            for j in range(len(thermistor_temp)):
                full_row += "," + str(thermistor_temp[j][i])
                
                
            writer.writerow(full_row)
            table[i] = full_row

def show_table():
    os.system('clear')
    for i in range(len(table)):
        print(table[i])


if __name__ == '__main__':
    main()