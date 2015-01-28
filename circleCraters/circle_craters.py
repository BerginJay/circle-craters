# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CircleCraters
                                 A QGIS plugin
 A crater counting tool for planetary science
                              -------------------
        begin                : 2014-12-31
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Sarah E Braden
        email                : braden.sarah@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, SIGNAL, Qt, QObject
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtGui import QMessageBox
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from circle_craters_dialog import CircleCratersDialog
import os.path
import rectangle_example

from qgis.gui import *
from qgis.core import *


class PointTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

    def canvasPressEvent(self, event):
        pass

    # def canvasMoveEvent(self, event):
    #     x = event.pos().x()
    #     y = event.pos().y()
    #     point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        print x
        print y
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        print point

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True


class CircleCraters:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # a reference to our map canvas (Return a pointer to the map canvas)
        self.canvas = self.iface.mapCanvas()
        # this QGIS tool emits as QgsPoint after each click
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CircleCraters_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = CircleCratersDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Circle Craters')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CircleCraters')
        self.toolbar.setObjectName(u'CircleCraters')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CircleCraters', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CircleCraters/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'A crater counting tool for planetary science'),
            callback=self.run,
            parent=self.iface.mainWindow()
        )
        # A good way to connect to signals in PyQt is using this syntax:
        # This line works!
        print self.clickTool.canvasClicked.connect(self.handleMouseDown)
        # rectangle_example.RectangleMapTool(self.canvas)

    def handleMouseDown(self, point, button):
        """signal canvasClicked() emits a QgsPoint. handleMouseDown() prints
        out the point???
        """
        print str(point.x()) + " , " + str(point.y())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Circle Craters'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # make our clickTool the tool that we'll use for now:
        # This line works:
        self.canvas.setMapTool(self.clickTool)

        # layers = QgsMapLayerRegistry.instance().mapLayers().values()

        # for layer in layers:
        #     if layer.type() == QgsMapLayer.VectorLayer:
        #         # User selects the layer that the crater polygons go into
        #         self.dlg.layerCombo.addItem(layer.name(), layer)

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Count the features in the vector layer previously selected
            # index = self.dlg.layerCombo.currentIndex()
            # layer = self.dlg.layerCombo.itemData(index)
            print "Done with this shit"

            # map_point = self.clickTool.toMapCoordinates(point)

            # connecting a slot to ClickTool canvasClicked() signal will let
            # you implement custom behaviour for the passed in point.
            # print SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)")

            # result = self.mouse_click_makes_point()

            # QMessageBox.information(
            #     self.iface.mainWindow(),
            #     "Info",
            #     "connect = %s" % str(result),
            # )
            pass



    # this QGIS tool emits as QgsPoint after each click (is a constructor)
    # self.clickTool = QgsMapToolEmitPoint(self.canvas)

    # signal canvasClicked() emits a QgsPoint.

    # Get three points from where the user clicks in x, y coordinates
    # point1 = QgsPoint(startPoint.x(), startPoint.y())
    # point2 = QgsPoint(startPoint.x(), endPoint.y())
    # point3 = QgsPoint(endPoint.x(), endPoint.y())
