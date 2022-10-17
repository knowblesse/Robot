using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.IO.Ports;

namespace RobotSerialController
{
    public partial class RobotSerialController : Form
    {
        // Constants
        SerialPort robot = new SerialPort();
        int forwardState = 0;
        int rightState = 0;

        public RobotSerialController()
        {
            
            InitializeComponent();
            comb_COM.DataSource = SerialPort.GetPortNames();
            btn_keyboard.KeyDown += new KeyEventHandler(listen_keyboard);

        }

        private void listen_keyboard(object sender, KeyEventArgs e)
        {
            switch(e.KeyData.ToString())
            {
                case "W":
                    btn_front_Click(null, null);
                    break;
                case "S":
                    btn_back_Click(null, null);
                    break ;
                case "D":
                    btn_right_Click(null, null);
                    break;
                case "A":
                    btn_left_Click(null, null);
                    break;
                case "X":
                    btn_stop_Click(null, null);
                    break;
            }
        }

        private void btn_refresh_Click(object sender, EventArgs e)
        {
            comb_COM.DataSource = SerialPort.GetPortNames();
        }

        private void btn_connect_Click(object sender, EventArgs e)
        {
            if (comb_COM.SelectedItem.ToString() != "")
            {
                robot.PortName = comb_COM.Text;
                robot.BaudRate = 57600;
                robot.DataBits = 8;
                robot.StopBits = StopBits.One;
                robot.Parity = Parity.None;
                if (cbox_receive.Checked)
                {
                    robot.DataReceived += new SerialDataReceivedEventHandler(robotDataReceived);
                }
                printOutput("Establishing Robot Connection...");
                printOutput("└Port Name : " + comb_COM.Text);
                printOutput("└BaudRate : " + robot.BaudRate.ToString());
                printOutput("└DataBits : " + robot.DataBits.ToString());
                printOutput("└StopBits : " + robot.StopBits.ToString());
                printOutput("└Parity : " + robot.Parity.ToString());

                try
                {
                    if(robot.IsOpen)
                    {
                        printOutput("Serial Port is already open.");
                        printOutput("Trying to close it first and reconnect.");
                        robot.Close();
                        robot.Open();
                        printOutput("Robot Connected!");
                        btn_connect.Enabled = false;
                    }
                    else
                    {
                        robot.Open();
                        printOutput("Robot Connected!");
                        btn_connect.Enabled = false;
                    }
                }
                catch (Exception ex)
                {
                    printOutput("Connection Error");
                    printOutput(ex.ToString());
                }
            }
            else
            {
                MessageBox.Show("Select COM port first!");
            }

        }
        private void robotDataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            this.Invoke(new EventHandler(printRobotOutput));
        }
        private void printRobotOutput(object s, EventArgs e)
        {
            int ReceiveData = robot.ReadByte();
            printOutput(string.Format("{0:X2}", ReceiveData));
        }

        private void btn_front_Click(object sender, EventArgs e)
        {
            robot.Write("w");
            printOutput("Command sent : w");
            forwardState++;
            updateStateLabel();
        }

        private void btn_stop_Click(object sender, EventArgs e)
        {
            robot.Write("x");
            printOutput("Command sent : x");
            forwardState = 0;
            rightState = 0;
            updateStateLabel();
        }
        private void btn_back_Click(object sender, EventArgs e)
        {
            robot.Write("s");
            printOutput("Command sent : s");
            forwardState--;
            updateStateLabel();
        }

        private void btn_right_Click(object sender, EventArgs e)
        {
            robot.Write("g");
            printOutput("Command sent : g");
            rightState++;
            updateStateLabel();
        }

        private void btn_left_Click(object sender, EventArgs e)
        {
            robot.Write("f");
            printOutput("Command sent : f");
            rightState--;
            updateStateLabel();
        }
        private void printOutput(string str)
        {
            textBox1.AppendText("[" + DateTime.Now.ToString("HH:MM:ss:fff") + "] " + str + "\r\n");
        }

        private void updateStateLabel()
        {
            lbl_foward.Text = forwardState.ToString();
            if(rightState == 0)
            {
                lbl_rotation.Text = "Stop";
            }
            else if (rightState > 0)
            {
                lbl_rotation.Text = "R" + rightState.ToString();
            }
            else
            {
                lbl_rotation.Text = "L" + (-rightState).ToString();
            }
        }

        private void btn_keyboard_focus(object sender, EventArgs e)
        {
            if(btn_keyboard.Focused)
            {
                btn_keyboard.BackColor = Color.CadetBlue;
            }
            else
            {
                btn_keyboard.BackColor = Color.IndianRed;
            }
        }

    }
}
