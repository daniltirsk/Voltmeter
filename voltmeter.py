import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import math
import numpy as np
import time

def period_change(node):
    global period
    period = int(dpg.get_value(node))
    dpg.set_item_label('series_tag',f"Mean voltage over {period}s period")
    reset()

def span_change(node):
    global span
    span = int(dpg.get_value(node))
    dpg.set_axis_limits('x_axis', 0, span)

def reset():
    global min_voltage,avg_voltage,max_voltage,mean_voltages

    min_voltage,avg_voltage,max_voltage = 0,0,0
    mean_voltages = []


def _hsv_to_rgb(h, s, v):
    if s == 0.0: return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
    if i == 0: return (255*v, 255*t, 255*p)
    if i == 1: return (255*q, 255*v, 255*p)
    if i == 2: return (255*p, 255*v, 255*t)
    if i == 3: return (255*p, 255*q, 255*v)
    if i == 4: return (255*t, 255*p, 255*v)
    if i == 5: return (255*v, 255*p, 255*q)

def draw_volt(val, size = 20):
    string = f"{round(val, 1)}V"
    dpg.draw_text([-len(string)*size/4, -size/2], string, size=size, color=[0, 0, 0], parent='volt_text_node', tag='volt_text')

def draw_volt_stats(min_volt=0, avg_volt=5, max_volt=10):
    size = 24

    dpg.draw_text([-170, 85], f"MIN:{round(min_volt,1)}V", size=size, color=[0, 255, 255],
                  parent='volt_text_node', tag='volt_text_min')
    dpg.draw_text([-50, 85], f"AVG:{round(avg_volt,1)}V", size=size, color=[0, 255, 255],
                  parent='volt_text_node', tag='volt_text_avg')
    dpg.draw_text([70, 85], f"MAX:{round(max_volt,1)}V", size=size, color=[0, 255, 255],
                  parent='volt_text_node', tag='volt_text_max')

def hand_ratation(voltages, volt_transition):
    last_time, last_rot = dpg.get_item_user_data("hand_node")

    if len(volt_transition) > 0:
        hand_rot = volt_transition.pop(0)
        dpg.apply_transform("hand_node", dpg.create_rotation_matrix(math.pi * hand_rot / 180.0, [0, 0, -1]))
    elif time.time() - last_time >= 0.1:
        voltage = np.random.normal(loc=5, scale=5 / 4)
        voltages.append(voltage)
        hand_rot = num_of_ticks * tick_angle + start_angle - voltage * 20
        volt_transition.extend(list(np.interp([i for i in range(0, 11)], [0, 10], [last_rot, hand_rot])))

        last_time = time.time()
        last_rot = hand_rot

        dpg.delete_item('volt_text')
        draw_volt(voltage)

    dpg.set_item_user_data("hand_node", [last_time, last_rot])

def series_update(mean_voltages, voltages, span):
    last_time = dpg.get_item_user_data("series_tag")
    if time.time() - last_time >= period:
        mean_voltages.append(np.mean(voltages))
        last_time = time.time()
        voltages.clear()

        dpg.delete_item('volt_text_min')
        dpg.delete_item('volt_text_avg')
        dpg.delete_item('volt_text_max')
        draw_volt_stats(min(mean_voltages),np.mean(mean_voltages),max(mean_voltages))

    dpg.set_item_user_data("series_tag", last_time)

    if len(mean_voltages) > 100:
        mean_voltages.pop(0)

    x = [i for i in range(0,min(span,len(mean_voltages)))]
    dpg.set_value('series_tag', [x, mean_voltages[max(-span,-len(mean_voltages)):]])


dpg.create_context()
dpg.create_viewport(title='Voltmeter',width=430,height=800,resizable=False)


start_angle = -10
cur_angle = start_angle
tick_angle = 4
num_of_ticks = 50

last_time = time.time()
period = 1
span = 20

min_voltage = 0
max_voltage = 10
avg_voltage = 5

with dpg.window(label="VoltmeterTirsk", width=420, height=800, pos=(0, 0), tag="__demo_id",no_resize=True,no_move=True,no_close=True,no_collapse=True):
    with dpg.drawlist(tag='analog_meter', width=400, height=350):
        # with dpg.draw_node(tag='background'):
        #     dpg.draw_rectangle([0,0],[400,350], color=[0,0,0],fill=[0,0,0])
        with dpg.draw_node(tag="root_node"):
            with dpg.draw_node(tag="hand_node", user_data=[time.time(),0]):
                dpg.draw_circle([155, 0], 3, color=[255, 0, 0], fill=[0, 255, 255])
                dpg.draw_line([0, 0], [155, -0], thickness=3, color=[255, 255, 255])

            dpg.draw_circle([0, 0], 30, color=[0, 255, 255], fill=[255, 255, 255],thickness=10)

            dpg.draw_rectangle([-190, 75], [190, 120], color=[0, 255, 255], thickness=4)

            for i in range(num_of_ticks + 1):
                with dpg.draw_node():
                    if i % 10 == 0:
                        dpg.draw_line([130, 0], [155, 0], thickness=1, color=[255, 0, 0])
                        if cur_angle <= 90:
                            dpg.draw_text([180, 0], str(num_of_ticks*tick_angle // 20 - (cur_angle - start_angle) // 20), size=16)
                        else:
                            dpg.draw_text([180, -8], str(num_of_ticks*tick_angle // 20 - (cur_angle - start_angle) // 20), size=16)

                    elif i%5==0:
                        dpg.draw_line([130, 0], [153, 0], thickness=1, color=[255, 255, 255])
                    else:
                        dpg.draw_line([130, 0], [150, 0], thickness=1, color=[255, 255, 255])

                    dpg.apply_transform(dpg.last_container(), dpg.create_rotation_matrix(math.pi*cur_angle/180.0 , [0, 0, -1]))
                    cur_angle+=tick_angle

            with dpg.draw_node(tag='volt_text_node'):
                draw_volt(0)
                draw_volt_stats()

    with dpg.theme(tag="plot_theme"):
        with dpg.theme_component(dpg.mvLineSeries):
            dpg.add_theme_color(dpg.mvPlotCol_Line, (0, 255, 255), category=dpg.mvThemeCat_Plots)
            dpg.add_theme_style(dpg.mvPlotStyleVar_LineWeight,2, category=dpg.mvThemeCat_Plots)


    with dpg.group(tag='controls',horizontal=True, width=100):
        with dpg.theme(tag="button_theme" + str(i)):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, _hsv_to_rgb(4.2 / 7.0, 0.6, 0.6))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, _hsv_to_rgb(4.2 / 7.0, 0.8, 0.8))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, _hsv_to_rgb(4.2 / 7.0, 0.7, 0.7))
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4 * 5)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4 * 3, 4 * 3)

        dpg.add_button(label='RESET', callback=reset)
        dpg.bind_item_theme(dpg.last_item(), "button_theme" + str(i))
        dpg.add_listbox([1,5,10],label = 'Period', width=30, callback=period_change)
        dpg.add_listbox([20, 50, 100], label='Span', width=30, callback=span_change)

    with dpg.plot(label="line_series", height=300, width=400):
        dpg.add_plot_legend()

        dpg.add_plot_axis(dpg.mvXAxis, label="Time", tag="x_axis")
        dpg.add_plot_axis(dpg.mvYAxis, label="Voltage", tag="y_axis")

        dpg.add_line_series([], [], label=f"Mean voltage over {period}s period", parent="y_axis", tag="series_tag", user_data=0)
        dpg.set_axis_limits('y_axis',0,10)
        dpg.set_axis_limits('x_axis',0,span)

        dpg.bind_item_theme("series_tag", "plot_theme")





distance = 100
dpg.apply_transform("root_node", dpg.create_translation_matrix([200, 200]))
dpg.apply_transform("hand_node", dpg.create_rotation_matrix(math.pi * (num_of_ticks*tick_angle+start_angle) / 180.0, [0, 0, -1]))


voltages = []
mean_voltages = []
volt_transition = []

with dpg.item_handler_registry(tag="hand_rotation_anim"):
    dpg.add_item_visible_handler(callback= lambda x: hand_ratation(voltages,volt_transition))
    dpg.add_item_visible_handler(callback=lambda x: series_update(mean_voltages, voltages, span))

dpg.bind_item_handler_registry("analog_meter",  "hand_rotation_anim")


dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()