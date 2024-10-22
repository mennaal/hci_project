using System;
using System.Windows.Forms;

namespace ZooEncyclopedia
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Form1()); // Ensure this references Form1
        }
    }
}
