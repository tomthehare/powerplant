from gpiozero import CPUTemperature


def take_temperature():
    cpu = CPUTemperature()
    print(cpu.temperature)
    
    
take_temperature()