function Main() {
    // // Need to start up Schematic Server first.
    // Client.StartServer("SCH")

    var SheetFileName = "test_3.SchDoc"
    SchSheet = Client.OpenDocument("Sch", SheetFileName)

    var Workspace = GetWorkspace
    if(!Workspace) ShowMessage("Workspace not available!")
    Workspace.DM_FocusedProject.DM_AddSourceDocument(SchSheet.FileName)

    Client.ShowDocument(SchSheet)
    if (!SchServer) ShowMessage("SCH server not available!")
    SchDoc = SchServer.GetCurrentSchDocument;

    var IntMan = IntegratedLibraryManager
    if (!IntMan) ShowMessage("IntegratedLibraryManager not available!")

    // ---- Init robots in Schematic editor
    SchServer.ProcessControl.PreProcess(SchSheet, '');

    // ----- Check libraries
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
    var nConnectors = 1 // 24
    var conn_name = 'PANASONIC_AXK6SA3677YG'
    var conn_lib_index = 6
    var conn_sep = 150
    var conn_width = 30
    var conn_pin_xOffset = 20 
    var conn_pin_gap = 10 
    var x0_conn = 100
    var y0_conn = 720

    var wire_length = 40

    var nPads = 128 // 128
    var pad_name = 'PLATED_HOLE0.5_PAD1.5'
    var pad_lib_index = 7

    for (var iconn = 0; iconn < nConnectors; iconn++) {
        var x_conn = x0_conn + iconn*conn_sep
        var y_conn = y0_conn
        var conn_label = 'C'+ (iconn+1)
        IntMan.PlaceLibraryComponent(
            conn_name, 
            IntMan.AvailableLibraryPath(conn_lib_index),
            'Designator=' + conn_label +'|Location.X='+ x_conn*1e5 +'|Location.Y='+y_conn*1e5)
        for (var ipad = 0; ipad < nPads/2; ipad++) {
            var x_lpad = x_conn - conn_pin_xOffset - wire_length
            var x_rpad = x_lpad + conn_width + 2*conn_pin_xOffset + 2*wire_length
            var y_pad = y_conn - (ipad+1)*conn_pin_gap

            // connect left pad 
            var pad_label = 'V'+ (iconn+1) +'_'+ ((ipad+1)*2-1)
            // IntMan.PlaceLibraryComponent(
            //     pad_name, 
            //     IntMan.AvailableLibraryPath(pad_lib_index),
            //     'Designator='+ pad_label +'|Location.X='+ x_lpad*1e5 +'|Location.Y='+ y_pad*1e5) 

            var SchWire = SchServer.SchObjectFactory(eWire,eCreate_GlobalCopy)
            SchWire.SetState_LineWidth = eSmall
            SchWire.Location = Point(x_lpad*1e5, y_pad*1e5);
            SchWire.InsertVertex = 1;
            SchWire.SetState_Vertex(1, Point(x_lpad*1e5, y_pad*1e5));
            SchWire.InsertVertex = 2;
            SchWire.SetState_Vertex(2, Point((x_lpad+wire_length)*1e5, y_pad*1e5));
            SchDoc.RegisterSchObjectInContainer(SchWire)

            SchNetlabel = SchServer.SchObjectFactory(eNetlabel,eCreate_GlobalCopy);
            SchNetlabel.Location    = Point(x_lpad*1e5, y_pad*1e5);
            SchNetlabel.Orientation = eRotate0;
            SchNetlabel.Text        = conn_label+'-'+pad_label;
            SchDoc.RegisterSchObjectInContainer(SchNetlabel);

            // connect right pad
            pad_label = 'V'+ (iconn+1) +'_'+ (ipad+1)*2
            // IntMan.PlaceLibraryComponent(
            //     pad_name, 
            //     IntMan.AvailableLibraryPath(pad_lib_index),
            //     'Designator='+ pad_label +'|Mirrored|Location.X='+ x_rpad*1e5 +'|Location.Y='+ y_pad*1e5)    

            SchWire = SchServer.SchObjectFactory(eWire,eCreate_GlobalCopy)
            SchWire.SetState_LineWidth = eSmall
            SchWire.Location = Point(x_rpad*1e5, y_pad*1e5);
            SchWire.InsertVertex = 1;
            SchWire.SetState_Vertex(1, Point(x_rpad*1e5, y_pad*1e5));
            SchWire.InsertVertex = 2;
            SchWire.SetState_Vertex(2, Point((x_rpad-wire_length)*1e5, y_pad*1e5));
            SchDoc.RegisterSchObjectInContainer(SchWire)

            SchNetlabel = SchServer.SchObjectFactory(eNetlabel,eCreate_GlobalCopy);
            SchNetlabel.Location    = Point(x_rpad*1e5, y_pad*1e5);
            SchNetlabel.Orientation = eRotate0;
            SchNetlabel.Text        = conn_label+'-'+pad_label;
            SchDoc.RegisterSchObjectInContainer(SchNetlabel);
        }
    }

    // ---- Clean robots and refresh screen
    SchServer.ProcessControl.PostProcess(SchSheet, '');
    SchDoc.GraphicallyInvalidate
    return
}
