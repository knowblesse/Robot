using System.Drawing;

namespace RobotSerialController
{
    partial class RobotSerialController
    {
        /// <summary>
        /// 필수 디자이너 변수입니다.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 사용 중인 모든 리소스를 정리합니다.
        /// </summary>
        /// <param name="disposing">관리되는 리소스를 삭제해야 하면 true이고, 그렇지 않으면 false입니다.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form 디자이너에서 생성한 코드

        /// <summary>
        /// 디자이너 지원에 필요한 메서드입니다. 
        /// 이 메서드의 내용을 코드 편집기로 수정하지 마세요.
        /// </summary>
        private void InitializeComponent()
        {
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(RobotSerialController));
            this.btn_refresh = new System.Windows.Forms.Button();
            this.comb_COM = new System.Windows.Forms.ComboBox();
            this.btn_connect = new System.Windows.Forms.Button();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.btn_front = new System.Windows.Forms.Button();
            this.btn_back = new System.Windows.Forms.Button();
            this.btn_left = new System.Windows.Forms.Button();
            this.btn_right = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.lbl_foward = new System.Windows.Forms.Label();
            this.lbl_rotation = new System.Windows.Forms.Label();
            this.cbox_receive = new System.Windows.Forms.CheckBox();
            this.btn_stop = new System.Windows.Forms.Button();
            this.btn_keyboard = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // btn_refresh
            // 
            this.btn_refresh.Location = new System.Drawing.Point(169, 41);
            this.btn_refresh.Name = "btn_refresh";
            this.btn_refresh.Size = new System.Drawing.Size(75, 23);
            this.btn_refresh.TabIndex = 0;
            this.btn_refresh.Text = "Refresh";
            this.btn_refresh.UseVisualStyleBackColor = true;
            this.btn_refresh.Click += new System.EventHandler(this.btn_refresh_Click);
            // 
            // comb_COM
            // 
            this.comb_COM.FormattingEnabled = true;
            this.comb_COM.Location = new System.Drawing.Point(22, 43);
            this.comb_COM.Name = "comb_COM";
            this.comb_COM.Size = new System.Drawing.Size(121, 20);
            this.comb_COM.TabIndex = 1;
            // 
            // btn_connect
            // 
            this.btn_connect.Location = new System.Drawing.Point(261, 41);
            this.btn_connect.Name = "btn_connect";
            this.btn_connect.Size = new System.Drawing.Size(75, 23);
            this.btn_connect.TabIndex = 2;
            this.btn_connect.Text = "Connect";
            this.btn_connect.UseVisualStyleBackColor = true;
            this.btn_connect.Click += new System.EventHandler(this.btn_connect_Click);
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(12, 350);
            this.textBox1.Multiline = true;
            this.textBox1.Name = "textBox1";
            this.textBox1.ReadOnly = true;
            this.textBox1.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.textBox1.Size = new System.Drawing.Size(323, 183);
            this.textBox1.TabIndex = 3;
            // 
            // btn_front
            // 
            this.btn_front.Location = new System.Drawing.Point(145, 138);
            this.btn_front.Name = "btn_front";
            this.btn_front.Size = new System.Drawing.Size(75, 68);
            this.btn_front.TabIndex = 4;
            this.btn_front.Text = "Front";
            this.btn_front.UseVisualStyleBackColor = true;
            this.btn_front.Click += new System.EventHandler(this.btn_front_Click);
            // 
            // btn_back
            // 
            this.btn_back.Location = new System.Drawing.Point(145, 274);
            this.btn_back.Name = "btn_back";
            this.btn_back.Size = new System.Drawing.Size(75, 68);
            this.btn_back.TabIndex = 5;
            this.btn_back.Text = "Back";
            this.btn_back.UseVisualStyleBackColor = true;
            this.btn_back.Click += new System.EventHandler(this.btn_back_Click);
            // 
            // btn_left
            // 
            this.btn_left.Location = new System.Drawing.Point(64, 206);
            this.btn_left.Name = "btn_left";
            this.btn_left.Size = new System.Drawing.Size(75, 68);
            this.btn_left.TabIndex = 6;
            this.btn_left.Text = "Left";
            this.btn_left.UseVisualStyleBackColor = true;
            this.btn_left.Click += new System.EventHandler(this.btn_left_Click);
            // 
            // btn_right
            // 
            this.btn_right.Location = new System.Drawing.Point(226, 206);
            this.btn_right.Name = "btn_right";
            this.btn_right.Size = new System.Drawing.Size(75, 68);
            this.btn_right.TabIndex = 7;
            this.btn_right.Text = "Right";
            this.btn_right.UseVisualStyleBackColor = true;
            this.btn_right.Click += new System.EventHandler(this.btn_right_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("굴림", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.label1.Location = new System.Drawing.Point(12, 84);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(80, 16);
            this.label1.TabIndex = 8;
            this.label1.Text = "Foward =";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("굴림", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.label2.Location = new System.Drawing.Point(12, 107);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(91, 16);
            this.label2.TabIndex = 9;
            this.label2.Text = "Rotation =";
            // 
            // lbl_foward
            // 
            this.lbl_foward.AutoSize = true;
            this.lbl_foward.Font = new System.Drawing.Font("굴림", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.lbl_foward.Location = new System.Drawing.Point(98, 84);
            this.lbl_foward.Name = "lbl_foward";
            this.lbl_foward.Size = new System.Drawing.Size(16, 16);
            this.lbl_foward.TabIndex = 8;
            this.lbl_foward.Text = "0";
            // 
            // lbl_rotation
            // 
            this.lbl_rotation.AutoSize = true;
            this.lbl_rotation.Font = new System.Drawing.Font("굴림", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(129)));
            this.lbl_rotation.Location = new System.Drawing.Point(109, 107);
            this.lbl_rotation.Name = "lbl_rotation";
            this.lbl_rotation.Size = new System.Drawing.Size(16, 16);
            this.lbl_rotation.TabIndex = 8;
            this.lbl_rotation.Text = "0";
            // 
            // cbox_receive
            // 
            this.cbox_receive.AutoSize = true;
            this.cbox_receive.Enabled = false;
            this.cbox_receive.Location = new System.Drawing.Point(169, 84);
            this.cbox_receive.Name = "cbox_receive";
            this.cbox_receive.Size = new System.Drawing.Size(145, 16);
            this.cbox_receive.TabIndex = 10;
            this.cbox_receive.Text = "Receive Robot Output";
            this.cbox_receive.UseVisualStyleBackColor = true;
            // 
            // btn_stop
            // 
            this.btn_stop.Location = new System.Drawing.Point(145, 206);
            this.btn_stop.Name = "btn_stop";
            this.btn_stop.Size = new System.Drawing.Size(75, 68);
            this.btn_stop.TabIndex = 4;
            this.btn_stop.Text = "Stop";
            this.btn_stop.UseVisualStyleBackColor = true;
            this.btn_stop.Click += new System.EventHandler(this.btn_stop_Click);
            // 
            // btn_keyboard
            // 
            this.btn_keyboard.BackColor = System.Drawing.Color.IndianRed;
            this.btn_keyboard.Location = new System.Drawing.Point(258, 283);
            this.btn_keyboard.Name = "btn_keyboard";
            this.btn_keyboard.Size = new System.Drawing.Size(77, 51);
            this.btn_keyboard.TabIndex = 11;
            this.btn_keyboard.Text = "Start Keyboard";
            this.btn_keyboard.UseVisualStyleBackColor = false;
            this.btn_keyboard.GotFocus += new System.EventHandler(this.btn_keyboard_focus);
            this.btn_keyboard.LostFocus += new System.EventHandler(this.btn_keyboard_focus);
            // 
            // RobotSerialController
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(347, 545);
            this.Controls.Add(this.btn_keyboard);
            this.Controls.Add(this.cbox_receive);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.lbl_rotation);
            this.Controls.Add(this.lbl_foward);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.btn_right);
            this.Controls.Add(this.btn_left);
            this.Controls.Add(this.btn_back);
            this.Controls.Add(this.btn_stop);
            this.Controls.Add(this.btn_front);
            this.Controls.Add(this.textBox1);
            this.Controls.Add(this.btn_connect);
            this.Controls.Add(this.comb_COM);
            this.Controls.Add(this.btn_refresh);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "RobotSerialController";
            this.Text = "RobotSerialController";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button btn_refresh;
        private System.Windows.Forms.ComboBox comb_COM;
        private System.Windows.Forms.Button btn_connect;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.Button btn_front;
        private System.Windows.Forms.Button btn_back;
        private System.Windows.Forms.Button btn_left;
        private System.Windows.Forms.Button btn_right;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label lbl_foward;
        private System.Windows.Forms.Label lbl_rotation;
        private System.Windows.Forms.CheckBox cbox_receive;
        private System.Windows.Forms.Button btn_stop;
        private System.Windows.Forms.Button btn_keyboard;
    }
}

