from sardana.macroserver.macro import Macro, Hookable

XML = """
<sequence>
<macro name="MyMacro">
  <macro name="MyHook2">
    <hookPlace>my-hook-place</hookPlace>
  </macro>
</macro>
</sequence>
"""

# macro to be attached as general hook
class MyHook1(Macro):

    def run(self):
        self.output("In MyHook1")


# macro to be attached in the XML 
class MyHook2(Macro):

    def run(self):
        self.output("In MyHook2")


# macro to which we will attach hooks
class MyMacro(Macro, Hookable):

    hints = {"allowsHooks": ("my-hook-place",)}

    def run(self):
        self.output("In MyMacro")
        for hook in self.getHooks("my-hook-place"):
            hook()


# macro wrapper where we programmatically attach hook
class MyMacroWrapper(Macro):

    def run(self):
        self.output("In MyMacroWrapper")
        my_macro, _ = self.createMacro("MyMacro")
        my_macro.hooks = [(self.my_hook2, ["my-hook-place"])]
        self.runMacro(my_macro)

    def my_hook2(self):
        self.output("In my_hook2")

if __name__ == "__main__":
    import sys
    import lxml
    import taurus
    from sardana.taurus.core.tango.sardana.macroserver import registerExtensions
    registerExtensions()
    if len(sys.argv) < 2:
        print "Usage: python generalHooks <door name>"
        sys.exit(1)
    door_name = sys.argv[1]
    door = taurus.Device(door_name)
    door.runMacro("senv GeneralHooks {'my-hook-place':'MyHook1'}",
                  synch=True)
    xml = lxml.etree.fromstring(XML)
    door.runMacro(xml, synch=True)
    door.runMacro("MyMacroWrapper", synch=True)
