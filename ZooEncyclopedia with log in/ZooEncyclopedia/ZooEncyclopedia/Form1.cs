
using System;
using System.Collections.Generic;
using System.Net.Sockets;
using System.Drawing;
using System.Text;
using System.Linq;
using System.Windows.Forms;
using System.Threading;
using TUIO;

namespace ZooEncyclopedia
{
    public partial class Form1 : Form, TuioListener
    {
        private List<Animal> animals;
        private List<Animal> activeAnimals = new List<Animal>();
        private Animal draggedAnimal;
        private TuioClient tuioClient;
        private string feedbackMessage;
        private Brush feedbackBrush;
        private System.Windows.Forms.Timer feedbackTimer;
        private int messageDuration = 2000;
        private bool allAnimalsCorrect = false;
        private bool isGameStarted = false;
        private int selectedAnimalIndex = -1;
        private string finalMessage;
        private float angle = 0;
        private float angleIncrement = 5f;
        private const int menuRadius = 200;

        public Form1()
        {
            InitializeComponent();
            DoubleBuffered = true;
            InitializeAnimals();
            InitializeFeedback(); // Initialize feedback in constructor
            StartTUIOClient();
            InitializeInstructions();
            InitializeLoginFeedback();
            Load += Form1_Load;
            this.Text = "Zoo Encyclopedia Game";
            this.Size = new Size(800, 600);
            SetDefaultBackground(); // Initialize default background
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            Thread clientThread = new Thread(StartClient);
            clientThread.IsBackground = true;
            clientThread.Start();
        }

        private void StartClient()
        {
            Client client = new Client();
            if (client.ConnectToSocket("localhost", 5000))
            {
                while (true)
                {
                    string message = client.ReceiveMessage();
                    if (!string.IsNullOrEmpty(message))
                    {
                        Invoke((MethodInvoker)delegate
                        {
                            MessageBox.Show(message, "Bluetooth Scanner", MessageBoxButtons.OK, MessageBoxIcon.Information);
                        });
                    }
                }
            }
        }
        public class Client
        {
            private TcpClient _client;
            private NetworkStream _stream;

            public bool ConnectToSocket(string host, int portNumber)
            {
                try
                {
                    _client = new TcpClient(host, portNumber);
                    _stream = _client.GetStream();
                    Console.WriteLine("Connected to the Python server.");
                    return true;
                }
                catch (SocketException e)
                {
                    Console.WriteLine("Connection failed: " + e.Message);
                    return false;
                }
            }

            public string ReceiveMessage()
            {
                try
                {
                    byte[] buffer = new byte[1024];
                    int bytesReceived = _stream.Read(buffer, 0, buffer.Length);
                    return Encoding.UTF8.GetString(buffer, 0, bytesReceived);
                }
                catch (Exception e)
                {
                    Console.WriteLine("Error receiving message: " + e.Message);
                    return null;
                }
            }
        }
    
    private void InitializeFeedback()
        {
            feedbackMessage = "Welcome to the Zoo Encyclopedia Game! Select an animal from the menu to start.";
            feedbackBrush = Brushes.Blue;

            feedbackTimer = new System.Windows.Forms.Timer();
            feedbackTimer.Interval = messageDuration;
            feedbackTimer.Tick += feedbackTimer_Tick;
            feedbackTimer.Start();
        }

        private void InitializeInstructions()
        {
            feedbackMessage = "Welcome to the Zoo Encyclopedia Game! Select an animal from the menu to start.";
            feedbackBrush = Brushes.Blue;
            feedbackTimer.Start();
        }

        private void InitializeLoginFeedback()
        {
            feedbackMessage = "Please log in to start the game.";
            feedbackBrush = Brushes.Gray;
            feedbackTimer.Start();
        }

        private void InitializeAnimals()
        {
            animals = new List<Animal>
            {
                new Animal
                {
                    MarkerId = 1,
                    Name = "Lion",
                    Position = new Point(600, 50),
                    HousePosition = new Point(600, 50),
                    AnimalImage = LoadImage("lion.jpg"),
                    HouseImage = LoadImage("lion den.jpg"),
                    BackgroundImage = LoadImage("1.jpg"),
                },
                new Animal
                {
                    MarkerId = 2,
                    Name = "Monkey",
                    Position = new Point(600, 250),
                    HousePosition = new Point(600, 250),
                    AnimalImage = LoadImage("monky.jpg"),
                    HouseImage = LoadImage("monky tree2.jpg"),
                    BackgroundImage = LoadImage("2.jpg"),
                },
                new Animal
                {
                    MarkerId = 3,
                    Name = "Polar Bear",
                    Position = new Point(600, 400),
                    HousePosition = new Point(600, 400),
                    AnimalImage = LoadImage("polar bears.jpg"),
                    HouseImage = LoadImage("polar bear den.png"),
                    BackgroundImage = LoadImage("3.jpeg"),
                },
            };
        }

        private Image LoadImage(string path)
        {
            try
            {
                return Image.FromFile(path);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading image '{path}': {ex.Message}");
                return null;
            }
        }

        private void StartTUIOClient()
        {
            tuioClient = new TuioClient(3333);
            tuioClient.addTuioListener(this);
            tuioClient.connect();
        }

        public void addTuioObject(TuioObject to)
        {
            if (!isGameStarted && to.SymbolID == 11) // Rotate menu
            {
                angle += angleIncrement;
                if (angle >= 360) angle = 0;
                Invalidate();
                return;
            }

            if (!isGameStarted && to.SymbolID == 12) // Select animal from menu
            {
                var unplacedAnimals = animals.FindAll(a => !a.IsInCorrectHouse);

                if (unplacedAnimals.Count > 0)
                {
                    selectedAnimalIndex = (int)((angle / 360) * unplacedAnimals.Count) % unplacedAnimals.Count;
                    var selectedAnimal = unplacedAnimals[selectedAnimalIndex];

                    UpdateBackgroundImage(selectedAnimal); // Update background on selection

                    if (!activeAnimals.Contains(selectedAnimal))
                    {
                        activeAnimals.Add(selectedAnimal);
                    }

                    feedbackMessage = $"{selectedAnimal.Name} selected!";
                    feedbackBrush = Brushes.Green;
                    feedbackTimer.Start();
                    isGameStarted = true;

                    Invalidate();
                }
                return;
            }

            if (isGameStarted && selectedAnimalIndex != -1)
            {
                var selectedAnimal = activeAnimals.Last();
                if (selectedAnimal.MarkerId == to.SymbolID)
                {
                    int scaledX = (int)(to.X * this.ClientSize.Width);
                    int scaledY = (int)(to.Y * this.ClientSize.Height);
                    selectedAnimal.Position = new Point(scaledX, scaledY);
                    draggedAnimal = selectedAnimal;
                    Invalidate();
                }
            }
        }

        public void updateTuioObject(TuioObject to)
        {
            if (isGameStarted && selectedAnimalIndex != -1)
            {
                var selectedAnimal = animals[selectedAnimalIndex];
                if (selectedAnimal.MarkerId == to.SymbolID)
                {
                    int scaledX = (int)(to.X * this.ClientSize.Width);
                    int scaledY = (int)(to.Y * this.ClientSize.Height);
                    selectedAnimal.Position = new Point(scaledX, scaledY);
                    Invalidate();
                }
            }
        }

        public void removeTuioObject(TuioObject to)
        {
            if (isGameStarted && draggedAnimal != null && draggedAnimal.MarkerId == to.SymbolID)
            {
                CheckAnimalPlacement(draggedAnimal);
                draggedAnimal = null;
            }
        }

        public void addTuioBlob(TuioBlob tb) { }
        public void updateTuioBlob(TuioBlob tb) { }
        public void removeTuioBlob(TuioBlob tb) { }
        public void addTuioCursor(TuioCursor tc) { }
        public void updateTuioCursor(TuioCursor tc) { }
        public void removeTuioCursor(TuioCursor tc) { }
        public void refresh(TuioTime time) { }

        private void CheckAnimalPlacement(Animal animal)
        {
            if (IsAnimalInHouse(animal))
            {
                animal.Position = animal.HousePosition;
                animal.IsInCorrectHouse = true;
                SetFeedback($"{animal.Name} placed correctly!", Brushes.Green);

                selectedAnimalIndex = -1;
                isGameStarted = false;

                CheckCompletion();
                Invalidate();
            }
            else
            {
                animal.IsInCorrectHouse = false;
                SetFeedback("Wrong placement, try again!", Brushes.Red);
            }
        }

        private bool IsAnimalInHouse(Animal animal)
        {
            return (Math.Abs(animal.Position.X - animal.HousePosition.X) < 50 && Math.Abs(animal.Position.Y - animal.HousePosition.Y) < 50);
        }

        private void CheckCompletion()
        {
            if (animals.TrueForAll(a => a.IsInCorrectHouse) && !allAnimalsCorrect)
            {
                allAnimalsCorrect = true;
                finalMessage = "Great job, all is correct!";
                Invalidate();
            }
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);

            if (!isGameStarted)
            {
                DrawCircularMenu(e.Graphics);
                return;
            }

            DrawAnimals(e.Graphics);
            DrawHouses(e.Graphics);
            DrawFeedback(e.Graphics);

            if (allAnimalsCorrect)
            {
                e.Graphics.DrawString(finalMessage, new Font("Arial", 24, FontStyle.Bold), Brushes.Blue, this.ClientSize.Width / 2 - 200, this.ClientSize.Height / 2 + 150);
            }
        }

        private void DrawCircularMenu(Graphics g)
        {
            int menuCenterX = this.ClientSize.Width / 2;
            int menuCenterY = this.ClientSize.Height / 2;

            var unplacedAnimals = animals.FindAll(a => !a.IsInCorrectHouse);
            int count = unplacedAnimals.Count;

            for (int i = 0; i < count; i++)
            {
                float angleForAnimal = angle + (360f / count) * i;
                int x = menuCenterX + (int)(menuRadius * Math.Cos(angleForAnimal * Math.PI / 180));
                int y = menuCenterY + (int)(menuRadius * Math.Sin(angleForAnimal * Math.PI / 180));

                g.DrawImage(unplacedAnimals[i].AnimalImage, x - 50, y - 50, 100, 100);
            }
        }

        private void DrawAnimals(Graphics g)
        {
            foreach (var animal in activeAnimals)
            {
                g.DrawImage(animal.AnimalImage, animal.Position.X - 50, animal.Position.Y - 50, 100, 100);
            }
        }

        private void DrawHouses(Graphics g)
        {
            foreach (var animal in animals)
            {
                g.DrawImage(animal.HouseImage, animal.HousePosition.X - 50, animal.HousePosition.Y - 50, 100, 100);
            }
        }

        private void DrawFeedback(Graphics g)
        {
            g.DrawString(feedbackMessage, this.Font, feedbackBrush, 10, 10);
        }

        private void UpdateBackgroundImage(Animal animal)
        {
            this.BackgroundImage = animal.BackgroundImage;
            this.BackgroundImageLayout = ImageLayout.Stretch;
        }

        private void SetDefaultBackground()
        {
            this.BackgroundImage = LoadImage("zoo3.jpg");
            this.BackgroundImageLayout = ImageLayout.Stretch;
        }

        private void SetFeedback(string message, Brush color)
        {
            feedbackMessage = message;
            feedbackBrush = color;
            feedbackTimer.Start();
        }

        private void feedbackTimer_Tick(object sender, EventArgs e)
        {
            feedbackTimer.Stop();
            feedbackMessage = string.Empty;
            Invalidate();
        }
    }

    public class Animal
    {
        public int MarkerId { get; set; }
        public string Name { get; set; }
        public Point Position { get; set; }
        public Point HousePosition { get; set; }
        public Image AnimalImage { get; set; }
        public Image HouseImage { get; set; }
        public Image BackgroundImage { get; set; }
        public bool IsInCorrectHouse { get; set; } = false;
    }
}