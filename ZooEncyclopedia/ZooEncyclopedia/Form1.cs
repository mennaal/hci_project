using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;
using TUIO;

namespace ZooEncyclopedia
{
    public partial class Form1 : Form, TuioListener
    {
        private List<Animal> animals;
        private Animal draggedAnimal;
        private TuioClient tuioClient;
        private string feedbackMessage; 
        private Brush feedbackBrush; 
        private Timer feedbackTimer; 
        private int messageDuration = 2000; 
        private bool allAnimalsCorrect = false; 
        private bool isGameStarted = false; 
        private int loginMarkerId = 10; 
        private string finalMessage;
        private Timer loginFeedbackTimer; 

        public Form1()
        {
            InitializeComponent();
            DoubleBuffered = true; 
            InitializeAnimals();
            StartTUIOClient();
            InitializeInstructions();
            InitializeFeedback();
            InitializeLoginFeedback(); 
            this.BackgroundImage = Image.FromFile("zoo3.jpg");
            this.BackgroundImageLayout = ImageLayout.Stretch;
            this.Text = "Zoo Encyclopedia Game";
            this.Size = new Size(800, 600);
        }

        private void InitializeAnimals()
        {
            animals = new List<Animal>
            {
                new Animal
                {
                    MarkerId = 1,
                    Name = "Lion",
                    Position = new Point(50, 400), 
                    HousePosition = new Point(600, 50), 
                    AnimalImage = LoadImage("lion.jpg"),
                    HouseImage = LoadImage("lion den.jpg"),
                },
                new Animal
                {
                    MarkerId = 2,
                    Name = "Monkey",
                    Position = new Point(50, 250),
                    HousePosition = new Point(600, 250),
                    AnimalImage = LoadImage("monky.jpg"),
                    HouseImage = LoadImage("monky tree2.jpg"),
                },
                new Animal
                {
                    MarkerId = 3,
                    Name = "Polar Bear",
                    Position = new Point(50, 100),
                    HousePosition = new Point(600, 400),
                    AnimalImage = LoadImage("polar bears.jpg"),
                    HouseImage = LoadImage("polar bear den.png"),
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
            if (!isGameStarted)
            {
               
                if (to.SymbolID == loginMarkerId)
                {
                    isGameStarted = true; 
                    feedbackMessage = "Login Successful! Game Started!";
                    feedbackBrush = Brushes.Green;
                    feedbackTimer.Start(); 
                    loginFeedbackTimer.Start(); 
                    Invalidate();
                }
                else
                {
                    
                    feedbackMessage = "Incorrect Marker! Please Try Again.";
                    feedbackBrush = Brushes.Red;
                    feedbackTimer.Start(); // Display the error message
                    loginFeedbackTimer.Start(); // Start timer to clear message
                    Invalidate();
                }
                return;
            }

            foreach (var animal in animals)
            {
                if (animal.MarkerId == to.SymbolID)
                {
                    int scaledX = (int)(to.X * this.ClientSize.Width);
                    int scaledY = (int)(to.Y * this.ClientSize.Height);
                    animal.Position = new Point(scaledX, scaledY);
                    draggedAnimal = animal; 
                    break;
                }
            }
            Invalidate();
        }

        public void updateTuioObject(TuioObject to)
        {
            if (!isGameStarted) return;

            if (draggedAnimal != null && draggedAnimal.MarkerId == to.SymbolID)
            {
                int scaledX = (int)(to.X * this.ClientSize.Width);
                int scaledY = (int)(to.Y * this.ClientSize.Height);
                draggedAnimal.Position = new Point(scaledX, scaledY);
                Invalidate();
            }
        }

        public void removeTuioObject(TuioObject to)
        {
            if (!isGameStarted) return;

            if (draggedAnimal != null && draggedAnimal.MarkerId == to.SymbolID)
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
                e.Graphics.DrawString("Please place the login marker to start the game.", new Font("Arial", 24, FontStyle.Bold), Brushes.Black, this.ClientSize.Width / 2 - 370, this.ClientSize.Height / 2 - 50);
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

        private void DrawAnimals(Graphics g)
        {
            foreach (var animal in animals)
            {
                if (animal.AnimalImage != null)
                {
                    g.DrawImage(animal.AnimalImage, animal.Position.X, animal.Position.Y, 100, 100);
                    g.DrawString(animal.Name, this.Font, Brushes.Black, animal.Position.X, animal.Position.Y - 15);
                }
            }
        }

        private void DrawHouses(Graphics g)
        {
            foreach (var animal in animals)
            {
                if (animal.HouseImage != null)
                {
                    g.DrawImage(animal.HouseImage, animal.HousePosition.X, animal.HousePosition.Y, 100, 100);
                }
            }
        }

        private void CheckAnimalPlacement(Animal animal)
        {
            if (IsAnimalInHouse(animal))
            {
                animal.Position = animal.HousePosition; 
                animal.IsInCorrectHouse = true; 
                SetFeedback("Correct", Brushes.Green); 
            }
            else
            {
                animal.IsInCorrectHouse = false; 
                SetFeedback("Wrong", Brushes.Red); 
            }
            Invalidate(); 
            CheckCompletion(); 
        }

        private bool IsAnimalInHouse(Animal animal)
        {
            return (Math.Abs(animal.Position.X - animal.HousePosition.X) < 50 && Math.Abs(animal.Position.Y - animal.HousePosition.Y) < 50);
        }

        private void InitializeInstructions()
        {
            Label instructionsLabel = new Label
            {
                Text = "Drag the animals to their habitat!",
                Location = new Point(20, 20),
                Size = new Size(300, 30),
                Font = new Font("Arial", 12, FontStyle.Bold),
                ForeColor = Color.Black,
                BackColor = Color.Transparent
            };
            this.Controls.Add(instructionsLabel);
        }

        private void InitializeFeedback()
        {
            feedbackMessage = string.Empty; 
            feedbackBrush = Brushes.Transparent; 
            feedbackTimer = new Timer { Interval = messageDuration };
            feedbackTimer.Tick += (s, e) =>
            {
                feedbackMessage = string.Empty;
                feedbackBrush = Brushes.Transparent;
                feedbackTimer.Stop();
                Invalidate(); 
            };
        }

        private void InitializeLoginFeedback()
        {
            loginFeedbackTimer = new Timer { Interval = messageDuration };
            loginFeedbackTimer.Tick += (s, e) =>
            {
                feedbackMessage = string.Empty;
                feedbackBrush = Brushes.Transparent;
                loginFeedbackTimer.Stop();
                Invalidate(); 
            };
        }

        private void DrawFeedback(Graphics g)
        {
            if (!string.IsNullOrEmpty(feedbackMessage))
            {
                g.DrawString(feedbackMessage, new Font("Arial", 16, FontStyle.Bold), feedbackBrush, 100, 50);
            }
        }

        private void SetFeedback(string message, Brush color)
        {
            feedbackMessage = message;
            feedbackBrush = color;
            feedbackTimer.Start(); 
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
        public bool IsInCorrectHouse { get; set; }
    }
}

