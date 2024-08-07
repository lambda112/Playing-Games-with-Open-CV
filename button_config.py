def button_block(x,y, button_type = "old"):

    buttons_old = {
            0:((x - 100, 0 + 140), (x - 50, 0 + 190)), # button 0, wd
            1:((x - 170, 140), (x - 120, 0 + 190)), # button 1, w
            2:((x - 240, 140), (x - 190, 0 + 190)), # button 2, wa
            3:((x - 100, 0 + 210), (x - 50, 0 + 260)), # button 3, d
            4:((x - 240, 210), (x - 190, 0 + 260)), # button 4, a
            5:((x - 100, 0 + 280), (x - 50, 0 + 330)), # button 5, sd
            6:((x - 170, 280), (x - 120, 0 + 330)), # button 6, s
            7:((x - 240, 280), (x - 190, 0 + 330)), # button 7, sa
        }
     
    
    if button_type == "old":
        return buttons_old

