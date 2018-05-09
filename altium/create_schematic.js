function Main() {
    // // Need to start up Schematic Server first.
    Client.StartServer("SCH")

    // if I want to create a new sheet
    // var SheetFileName = "test.SchDoc"
    // var SchDoc = Client.OpenDocument("Sch", SheetFileName)
    // var Workspace = GetWorkspace
    // if(!Workspace) ShowMessage("Workspace not available!")
    // Workspace.DM_FocusedProject.DM_AddSourceDocument(SchDoc.FileName)
    // Client.ShowDocument(SchDoc)

    if (!SchServer) ShowMessage("SCH server not available!")
    var SchDoc = SchServer.GetCurrentSchDocument;
    var IntMan = IntegratedLibraryManager
    if (!IntMan) ShowMessage("IntegratedLibraryManager not available!")
    // ---- Init robots in Schematic editor
    SchServer.ProcessControl.PreProcess(SchDoc, '');

    //----- Check library contents
    // var str = 'Available libraries: \n'
    // for (var iLib=0; iLib<IntMan.AvailableLibraryCount(); iLib++){
    //     str += IntMan.AvailableLibraryPath(iLib)+' ->'
    //     for (var iComp=0; iComp<IntMan.GetComponentCount(IntMan.AvailableLibraryPath(iLib)); iComp++){
    //         if (iComp) str += ', '
    //         str += IntMan.GetComponentName(IntMan.AvailableLibraryPath(iLib),iComp)
    //     }
    //     str += '\n'
    // }   
    // ShowMessage(str)
    // return

    // ---- Place connectors and pads, add wires and assign net labels
    var nConnectors = 12
    var nPads = 156
    var conn_name = 'HIROSE_FX10A-140S/14-SV(71)'//'PANASONIC_AXK6SA3677YG'
    var conn_lib_index = 0
    var conn_sep = 230
    var conn_width = 40
    var conn_height = 900
    var conn_pin_xOffset = 20 
    var conn_pin_gap = 10 
    var x0_conn = 200
    var y0_conn = 2000

    var wire_length = 40

    for (var iconn = 0; iconn < nConnectors; iconn++) {
        var x_conn = x0_conn + (iconn%12)*conn_sep
        var y_conn = y0_conn - (conn_height)*(Math.floor(iconn/12))
        var conn_label = 'C'+ (iconn+1)
        IntMan.PlaceLibraryComponent(
            conn_name, 
            IntMan.AvailableLibraryPath(conn_lib_index),
            'Designator=' + conn_label +'|Location.X='+ x_conn*1e5 +'|Location.Y='+y_conn*1e5)
        var ivia = 1;
        for (var ipad = 1; ipad < nPads+1; ipad++) {
            if (ipad<7 || (ipad>148 && ipad<155)) continue;
            var x_pad = x_conn - conn_pin_xOffset - wire_length
            if (ipad%2==0) x_pad += conn_width + 2*conn_pin_xOffset + 2*wire_length
            var y_pad = y_conn - (Math.floor((ipad-1)/2)+1)*conn_pin_gap
            if (ipad>154) y_pad -= conn_pin_gap

            // connect left pad 
            var pad_label = 'V'+ (129-(ivia+1)/2)
            if (ipad%2==0) pad_label = 'V'+ (ivia/2)
            
            var SchWire = SchServer.SchObjectFactory(eWire,eCreate_GlobalCopy)
            SchWire.SetState_LineWidth = eSmall
            SchWire.Location = Point(x_pad*1e5, y_pad*1e5)
            SchWire.InsertVertex = 1
            SchWire.SetState_Vertex(1, Point(x_pad*1e5, y_pad*1e5))
            SchWire.InsertVertex = 2
            var _tmp_x = x_pad + wire_length
            if (ipad%2==0) _tmp_x -= 2*wire_length
            SchWire.SetState_Vertex(2, Point(_tmp_x*1e5, y_pad*1e5))
            SchDoc.RegisterSchObjectInContainer(SchWire)

            var SchNetlabel = SchServer.SchObjectFactory(eNetlabel,eCreate_GlobalCopy)
            if (ipad%2==1) _tmp_x -= wire_length
            else _tmp_x += 5
            SchNetlabel.Location    = Point(_tmp_x*1e5, y_pad*1e5)
            SchNetlabel.Orientation = eRotate0
            var _tmp_label = conn_label+'_'+pad_label
            if ((ipad-11)%22==0 || (ipad-12)%22==0 || ipad>154) _tmp_label = 'GND'
            SchNetlabel.Text        = _tmp_label
            SchDoc.RegisterSchObjectInContainer(SchNetlabel)

            if (_tmp_label != 'GND') ivia++;
        }
    }

    // ---- Clean robots and refresh screen
    SchServer.ProcessControl.PostProcess(SchDoc, '');
    SchDoc.GraphicallyInvalidate
    return
}
