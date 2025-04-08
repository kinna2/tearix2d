import os
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Line, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout

# Registering custom font, fallback to default font if not available
try:
    LabelBase.register(name='Orbitron', fn_regular='Orbitron-Regular.ttf')
except IOError:
    print("Orbitron font not found, using default font")

# Ensure the Kivy home directory exists
kivy_home_dir = '/storage/emulated/0/Tearix2D ORG/.kivy'
os.makedirs(kivy_home_dir, exist_ok=True)

# Custom Button with futuristic style and larger size
class FuturisticButton(Button):
    def __init__(self, **kwargs):
        super(FuturisticButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0.5)
        self.color = (0, 1, 1, 1)  # Cyan color
        self.font_name = 'Orbitron' if 'Orbitron-Regular.ttf' in os.listdir() else 'Roboto'
        self.font_size = 24  # Larger font size
        self.size_hint = (None, None)
        self.size = (200, 70)  # Larger size for touch-friendly buttons
        self.border = (15, 15, 15, 15)
        self.bind(on_press=self.on_press_animation)
        self.bind(on_enter=self.on_hover)
        self.bind(on_leave=self.on_leave)

    def on_press_animation(self, instance):
        anim = Animation(background_color=(0, 1, 1, 0.8), duration=0.1) + Animation(background_color=(0, 0, 0, 0.5), duration=0.1)
        anim.start(self)

    def on_hover(self, *args):
        anim = Animation(background_color=(0, 1, 1, 0.8), duration=0.1)
        anim.start(self)

    def on_leave(self, *args):
        anim = Animation(background_color=(0, 0, 0, 0.5), duration=0.1)
        anim.start(self)

class FuturisticPopup(Popup):
    def __init__(self, **kwargs):
        super(FuturisticPopup, self).__init__(**kwargs)
        self.background = ''
        self.background_color = (0, 0, 0, 0.5)
        self.separator_color = (0, 1, 1, 1)
        self.separator_height = 2
        self.title_align = 'center'
        self.title_font = 'Orbitron' if 'Orbitron-Regular.ttf' in os.listdir() else 'Roboto'
        self.title_color = (0, 1, 1, 1)
        self.title_size = 20

class ParallaxLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ParallaxLayout, self).__init__(**kwargs)
        with self.canvas.before:
            self.parallax_rect = Rectangle(source='parallax_background.png', size=Window.size)
            self.bind(pos=self.update_parallax, size=self.update_parallax)
        
    def update_parallax(self, *args):
        self.parallax_rect.pos = self.pos
        self.parallax_rect.size = self.size

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        
        # Main layout with background
        layout = ParallaxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add a title label
        title_label = Label(
            text="Welcome to Tearix2D!",
            font_size=48,
            size_hint=(1, None),
            height=100,
            font_name='Orbitron' if 'Orbitron-Regular.ttf' in os.listdir() else 'Roboto',
            color=(0, 1, 1, 1),
            bold=True,
            halign='center',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        layout.add_widget(title_label)
        
        # Use AnchorLayout to center the button
        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        
        new_project_button = FuturisticButton(
            text="Start Drawing",
            size_hint=(None, None),
            size=(300, 100),
            font_size=36
        )
        new_project_button.bind(on_release=self.start_drawing)
        
        anchor_layout.add_widget(new_project_button)
        layout.add_widget(anchor_layout)
        
        self.add_widget(layout)
    
    def start_drawing(self, instance):
        self.manager.current = 'drawing'
        
class BrushPreviewWidget(Widget):
    def __init__(self, **kwargs):
        super(BrushPreviewWidget, self).__init__(**kwargs)
        self.current_color = (0, 0, 0, 1)  # Default to black
        self.line_width = 2
        self.brush_type = 'Soft Brush'
        self.update_preview()
    
    def update_preview(self):
        self.canvas.clear()
        with self.canvas:
            Color(*self.current_color)
            Line(points=[20, self.center_y, self.width - 20, self.center_y], width=self.line_width)

    def set_tool(self, tool):
        self.brush_type = tool
        self.update_preview()

class CanvasWidget(Widget):
    def __init__(self, **kwargs):
        super(CanvasWidget, self).__init__(**kwargs)
        self.current_color = (0, 0, 0, 1)  # Default to black
        self.line_width = 2
        self.current_tool = 'Soft Brush'  # Default to Soft Brush
        self.undo_stack = []
        self.redo_stack = []
        self.keyframes = []
        self.playback_event = None
        
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Set the background color to white
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def new_canvas(self, width, height):
        self.canvas.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Set the background color to white
            self.rect = Rectangle(pos=self.pos, size=(width, height))
            self.bind(pos=self.update_rect, size=self.update_rect)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):  # Ensure drawing only occurs on the canvas
            self.undo_stack.append(self.canvas.children[:])
            self.redo_stack = []
            self.keyframes.append([])

            action = None
            if self.current_tool == 'Soft Brush':
                action = ('line', touch.x, touch.y, self.line_width, self.current_color)
            elif self.current_tool == 'Eraser':
                action = ('eraser', touch.x, touch.y, self.line_width)
            elif self.current_tool == 'Fill':
                self.canvas.clear()
                action = ('fill', self.current_color)
            
            if action:
                with self.canvas:
                    Color(*self.current_color if self.current_tool != 'Eraser' else (1, 1, 1, 1))
                    touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.line_width)
                self.keyframes[-1].append(action)
    
    def on_touch_move(self, touch):
        if 'line' in touch.ud and self.collide_point(*touch.pos):  # Ensure drawing only occurs on the canvas
            touch.ud['line'].points += [touch.x, touch.y]
            if self.current_tool in ['Soft Brush', 'Eraser']:
                action = ('line', touch.x, touch.y, self.line_width, self.current_color) if self.current_tool == 'Soft Brush' else ('eraser', touch.x, touch.y, self.line_width)
                self.keyframes[-1].append(action)

    def on_touch_up(self, touch):
        if 'line' in touch.ud:
            points = touch.ud['line'].points
            if len(points) >= 4:
                # Smooth the line using a spline interpolation
                from scipy.interpolate import splprep, splev
                import numpy as np

                x = points[0::2]
                y = points[1::2]
                tck, u = splprep([x, y], s=0)
                u_new = np.linspace(u.min(), u.max(), len(points) * 2)
                x_new, y_new = splev(u_new, tck)

                # Clear the old line and draw the smoothed line
                self.canvas.remove(touch.ud['line'])
                with self.canvas:
                    Color(*self.current_color if self.current_tool != 'Eraser' else (1, 1, 1, 1))
                    new_points = np.column_stack((x_new, y_new)).flatten().tolist()
                    Line(points=new_points, width=self.line_width)

    def set_tool(self, tool):
        self.current_tool = tool
        self.line_width = 5 if tool == 'Soft Brush' else 20 if tool == 'Eraser' else self.line_width
    
    def set_color(self, instance, value):
        self.current_color = value
    
    def clear_canvas(self):
        self.canvas.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)  # Set the background color to white
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_rect, size=self.update_rect)
        self.keyframes = []

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.canvas.children[:])
            last_action = self.undo_stack.pop()
            self.canvas.clear()
            with self.canvas.before:
                Color(1, 1, 1, 1)  # Set the background color to white
                self.rect = Rectangle(pos=self.pos, size=self.size)
                self.bind(pos=self.update_rect, size=self.update_rect)
            for action in last_action:
                self.canvas.add(action)
            if self.keyframes:
                self.keyframes.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.canvas.children[:])
            next_action = self.redo_stack.pop()
            self.canvas.clear()
            with self.canvas.before:
                Color(1, 1, 1, 1)  # Set the background color to white
                self.rect = Rectangle(pos=self.pos, size=self.size)
                self.bind(pos=self.update_rect, size=self.update_rect)
            for action in next_action:
                self.canvas.add(action)
    
    def start_playback(self):
        if self.playback_event is None:
            self.clear_canvas()
            self.playback_event = Clock.schedule_interval(self.play_keyframes, 0.1)

    def stop_playback(self):
        if self.playback_event is not None:
            self.playback_event.cancel()
            self.playback_event = None

    def play_keyframes(self, dt):
        if not self.keyframes:
            self.stop_playback()
            return

        keyframe = self.keyframes.pop(0)
        for action in keyframe:
            if action[0] == 'line':
                with self.canvas:
                    Color(*action[4])
                    Line(points=[action[1], action[2]], width=action[3])
            elif action[0] == 'eraser':
                with self.canvas:
                    Color(1, 1, 1, 1)
                    Line(points=[action[1], action[2]], width=action[3])
            elif action[0] == 'fill':
                self.canvas.clear()
                with self.canvas:
                    Color(*action[1])
                    self.rect = Rectangle(pos=self.pos, size=self.size)

class DrawingScreen(Screen):
    def __init__(self, **kwargs):
        super(DrawingScreen, self).__init__(**kwargs)
        
        self.brush_popup = None
        
        layout = ParallaxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Add top control panel
        top_panel = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=5, spacing=5)
        buttons = [
            ("File", self.show_file_options),
            ("Tools", self.show_tools),
            ("AI", self.show_ai_options),
            ("Layers", self.show_layers_control)
        ]
        for text, callback in buttons:
            btn = FuturisticButton(text=text)
            btn.size_hint = (None, None)
            btn.size = (150, 70)
            btn.bind(on_release=callback)
            top_panel.add_widget(btn)
        
        layout.add_widget(top_panel)
        
        self.canvas_widget = CanvasWidget()
        layout.add_widget(self.canvas_widget)

        # Create a lower panel with a red transparent background
        lower_panel = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), padding=5, spacing=5, pos_hint={'center_x': 0.5, 'center_y': 0.5})
        with lower_panel.canvas.before:
            Color(1, 0, 0, 0.3)  # Red transparent background
            self.rect = RoundedRectangle(size=lower_panel.size, pos=lower_panel.pos, radius=[10])
            lower_panel.bind(pos=self.update_rect, size=self.update_rect)

        scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, 70), bar_width=10)
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_x=None, padding=5, spacing=5)
        buttons_layout.bind(minimum_width=buttons_layout.setter('width'))
        
        self.brush_button = FuturisticButton(text='Soft Brush')
        self.brush_button.size_hint = (None, None)
        self.brush_button.size = (150, 70)
        self.brush_button.bind(on_release=self.show_brush_popup)
        buttons_layout.add_widget(self.brush_button)
        
        tool_buttons = [
            ("Eraser", lambda x: self.canvas_widget.set_tool('Eraser')),
            ("Color", self.show_color_picker),
            ("Clear", self.canvas_widget.clear_canvas),
            ("Undo", self.canvas_widget.undo),
            ("Redo", self.canvas_widget.redo),
            ("Play", self.canvas_widget.start_playback),
            ("Stop", self.canvas_widget.stop_playback)
        ]
        for text, callback in tool_buttons:
            btn = FuturisticButton(text=text)
            btn.size_hint = (None, None)
            btn.size = (150, 70)
            btn.bind(on_release=callback)
            buttons_layout.add_widget(btn)
        
        scroll_view.add_widget(buttons_layout)
        lower_panel.add_widget(scroll_view)
        layout.add_widget(lower_panel)
        
        # Add Keyframe Panel
        keyframe_panel = KeyframePanel(self.canvas_widget)
        layout.add_widget(keyframe_panel)
        
        self.add_widget(layout)
    
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def show_file_options(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        buttons = [
            ("New Project", self.new_project),
            ("Open Project", self.open_project),
            ("Save", self.save_canvas),
            ("Save As", self.save_as_canvas),
            ("Export", self.export_canvas),
            ("Back to Home", self.back_to_home)
        ]
        for text, callback in buttons:
            btn = FuturisticButton(text=text)
            btn.size_hint_y = None
            btn.height = 70
            btn.bind(on_release=callback)
            content.add_widget(btn)
        
        file_popup = FuturisticPopup(title='File Options', content=content, size_hint=(0.5, 0.5))
        file_popup.open()
    
    def new_project(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        width_input = TextInput(hint_text='Width', multiline=False, size_hint_y=None, height=70, background_color=(0, 0, 0, 0.3), cursor_color=(0, 1, 1, 1))
        height_input = TextInput(hint_text='Height', multiline=False, size_hint_y=None, height=70, background_color=(0, 0, 0, 0.3), cursor_color=(0, 1, 1, 1))
        create_button = FuturisticButton(text="Create")
        create_button.size_hint_y = None
        create_button.height = 70
        
        content.add_widget(width_input)
        content.add_widget(height_input)
        content.add_widget(create_button)
        
        new_project_popup = FuturisticPopup(title='New Project', content=content, size_hint=(0.5, 0.5))
        
        def create_canvas(instance):
            try:
                width = int(width_input.text)
                height = int(height_input.text)
                self.canvas_widget.new_canvas(width, height)
                new_project_popup.dismiss()
            except ValueError:
                pass
        
        create_button.bind(on_release=create_canvas)
        new_project_popup.open()
    
    def open_project(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        file_path_input = TextInput(hint_text='File Path', multiline=False, size_hint_y=None, height=70, background_color=(0, 0, 0, 0.3), cursor_color=(0, 1, 1, 1))
        open_button = FuturisticButton(text="Open")
        open_button.size_hint_y = None
        open_button.height = 70
        
        content.add_widget(file_path_input)
        content.add_widget(open_button)
        
        open_project_popup = FuturisticPopup(title='Open Project', content=content, size_hint=(0.5, 0.5))
        
        def open_file(instance):
            file_path = file_path_input.text
            self.load_canvas(file_path)
            open_project_popup.dismiss()
        
        open_button.bind(on_release=open_file)
        open_project_popup.open()
    
    def load_canvas(self, file_path):
        # Implement the logic to load the selected file into the canvas
        pass
    
    def save_canvas(self, instance):
        file_path = "default.tearix"  # You can use a default file path or prompt the user
        self.save_to_file(file_path)
    
    def save_to_file(self, file_path):
        # Implement actual file saving logic
        pass
    
    def save_as_canvas(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        file_path_input = TextInput(hint_text='File Path', multiline=False, size_hint_y=None, height=70, background_color=(0, 0, 0, 0.3), cursor_color=(0, 1, 1, 1))
        save_button = FuturisticButton(text="Save")
        save_button.size_hint_y = None
        save_button.height = 70
        
        content.add_widget(file_path_input)
        content.add_widget(save_button)
        
        save_as_popup = FuturisticPopup(title='Save As', content=content, size_hint=(0.5, 0.5))
        
        def save_file(instance):
            file_path = file_path_input.text
            self.save_to_file(file_path)
            save_as_popup.dismiss()
        
        save_button.bind(on_release=save_file)
        save_as_popup.open()
    
    def export_canvas(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        formats = ["PNG", "JPG", "GIF", "MP4", "SVG", "PSD"]
        for fmt in formats:
            btn = FuturisticButton(text=f"Export as {fmt}")
            btn.size_hint_y = None
            btn.height = 70
            btn.bind(on_release=lambda x, fmt=fmt: self.export_to_format(fmt))
            content.add_widget(btn)
        
        export_popup = FuturisticPopup(title='Export Options', content=content, size_hint=(0.5, 0.5))
        export_popup.open()
    
    def export_to_format(self, fmt):
        file_path = f"exported.{fmt.lower()}"
        # Export the file
        pass

    def show_tools(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        tools = [
            ("Brush", 'Soft Brush'),
            ("Eraser", 'Eraser'),
            ("Fill", 'Fill')
        ]
        for text, tool in tools:
            btn = FuturisticButton(text=text)
            btn.size_hint_y = None
            btn.height = 70
            btn.bind(on_release=lambda x, tool=tool: self.select_tool(tool))
            content.add_widget(btn)
        
        tools_popup = FuturisticPopup(title='Tools', content=content, size_hint=(0.5, 0.5))
        tools_popup.open()
    
    def select_tool(self, tool):
        self.canvas_widget.set_tool(tool)
        self.brush_button.text = tool
    
    def show_ai_options(self, instance):
        # Implement AI options popup
        pass
    
    def show_layers_control(self, instance):
        # Implement layers control popup
        pass
    
    def show_brush_popup(self, instance):
        if not self.brush_popup:
            brush_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
            brush_grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
            brush_grid.bind(minimum_height=brush_grid.setter('height'))
            brush_grid.height = 88  # Adjusted height to include preview

            brushes = ['Soft Brush']
            for brush in brushes:
                brush_box = BoxLayout(orientation='vertical', size_hint_y=None, height=88)
                btn = FuturisticButton(text=brush)
                btn.size_hint_y = None
                btn.height = 70
                btn.bind(on_release=lambda btn: self.select_brush(btn))
                
                preview = BrushPreviewWidget(size_hint_y=None, height=44)
                preview.set_tool(brush)
                
                brush_box.add_widget(btn)
                brush_box.add_widget(preview)
                brush_grid.add_widget(brush_box)
            
            brush_layout.add_widget(brush_grid)
            self.brush_popup = FuturisticPopup(title='Select Brush', content=brush_layout, size_hint=(0.8, 0.8))
        
        self.brush_popup.open()

    def select_brush(self, btn):
        self.canvas_widget.set_tool(btn.text)
        self.brush_button.text = btn.text
        self.brush_popup.dismiss()

    def show_color_picker(self, instance):
        color_picker = ColorPicker()
        popup = FuturisticPopup(title='Pick a Color', content=color_picker, size_hint=(0.8, 0.8))
        color_picker.bind(color=self.canvas_widget.set_color)
        popup.open()
    
    def back_to_home(self, instance):
        self.manager.current = 'home'
        
class KeyframePanel(BoxLayout):
    def __init__(self, canvas_widget, **kwargs):
        super(KeyframePanel, self).__init__(**kwargs)
        self.canvas_widget = canvas_widget
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        self.size_hint_y = None
        self.height = 300  # Increased height for a larger keyframe panel

        # Red transparent background
        with self.canvas.before:
            Color(1, 0, 0, 0.3)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
            self.bind(pos=self.update_rect, size=self.update_rect)

        controls_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=70, spacing=10)
        
        # Add keyframe button
        self.add_keyframe_button = FuturisticButton(text="+", size_hint=(None, None), size=(70, 70))
        self.add_keyframe_button.bind(on_release=self.add_keyframe)
        controls_layout.add_widget(self.add_keyframe_button)

        # Play button
        self.play_button = FuturisticButton(text="▶️", size_hint=(None, None), size=(70, 70))
        self.play_button.bind(on_release=self.play_animation)
        controls_layout.add_widget(self.play_button)

        self.add_widget(controls_layout)

        # Keyframe previews
        self.preview_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        self.add_widget(self.preview_layout)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def add_keyframe(self, instance):
        keyframe_preview = KeyframePreview(self.canvas_widget)
        self.preview_layout.add_widget(keyframe_preview)
        self.canvas_widget.keyframes.append(keyframe_preview)

    def play_animation(self, instance):
        self.canvas_widget.start_playback(instance)

class KeyframePreview(BoxLayout):
    def __init__(self, canvas_widget, **kwargs):
        super(KeyframePreview, self).__init__(**kwargs)
        self.canvas_widget = canvas_widget
        self.size_hint = (None, None)
        self.size = (100, 100)  # Increased size for better visibility
        self.preview_image = Image(size_hint=(1, 1))

        with self.canvas.before:
            Color(0, 0, 0, 0.5)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[10])
            self.bind(pos=self.update_rect, size=self.update_rect)

        self.add_widget(self.preview_image)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def update_preview(self):
        # Update the preview image with a snapshot of the canvas
        texture = self.canvas_widget.export_as_image().texture
        self.preview_image.texture = texture
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(DrawingScreen(name='drawing'))
        return sm

if __name__ == "__main__":
    MyApp().run()