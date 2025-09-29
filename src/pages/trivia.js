import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Paper,
  Button,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  CircularProgress
} from '@mui/material';

export default function Trivia() {
  const [gameState, setGameState] = useState('menu'); // 'menu', 'playing', 'finished'
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(30);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [username, setUsername] = useState('');
  const [showAnswer, setShowAnswer] = useState(false);
  const [lastAnswerResult, setLastAnswerResult] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [showLeaderboard, setShowLeaderboard] = useState(false);
  const [loading, setLoading] = useState(false);
  const [gameStartTime, setGameStartTime] = useState(null);

  // Timer effect
  useEffect(() => {
    let timer;
    if (gameState === 'playing' && timeLeft > 0 && !showAnswer) {
      timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
    } else if (timeLeft === 0 && gameState === 'playing' && !showAnswer) {
      handleTimeUp();
    }
    return () => clearTimeout(timer);
  }, [timeLeft, gameState, showAnswer]);

  // Load leaderboard on component mount
  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchQuestions = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/trivia/questions?count=10');
      const data = await response.json();
      
      if (data.success) {
        setQuestions(data.questions);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error fetching questions:', error);
      return false;
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/trivia/leaderboard');
      const data = await response.json();
      
      if (data.success) {
        setLeaderboard(data.leaderboard);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  const startGame = async () => {
    if (!username.trim()) {
      alert('Please enter your username!');
      return;
    }

    setLoading(true);
    const success = await fetchQuestions();
    
    if (success) {
      setGameState('playing');
      setCurrentQuestion(0);
      setScore(0);
      setCorrectAnswers(0);
      setTimeLeft(30);
      setGameStartTime(Date.now());
    } else {
      alert('Failed to load questions. Please try again.');
    }
    setLoading(false);
  };

  const submitAnswer = async (answer) => {
    if (showAnswer) return;
    
    setSelectedAnswer(answer);
    setShowAnswer(true);

    try {
      const response = await fetch('http://localhost:5000/api/trivia/submit-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question_id: questions[currentQuestion].id,
          answer: answer
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setLastAnswerResult(result);
        if (result.correct) {
          setScore(score + result.points_earned);
          setCorrectAnswers(correctAnswers + 1);
        } else {
          setScore(Math.max(0, score + result.points_earned));
        }
      }
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  const handleTimeUp = () => {
    setSelectedAnswer('');
    setShowAnswer(true);
    setLastAnswerResult({
      correct: false,
      correct_answer: questions[currentQuestion]?.correct_answer || 'A',
      points_earned: -10,
      explanation: 'Time\'s up! No answer was selected.'
    });
    setScore(Math.max(0, score - 10));
  };

  const nextQuestion = () => {
    if (currentQuestion + 1 < questions.length) {
      setCurrentQuestion(currentQuestion + 1);
      setTimeLeft(30);
      setSelectedAnswer('');
      setShowAnswer(false);
      setLastAnswerResult(null);
    } else {
      finishGame();
    }
  };

  const finishGame = async () => {
    const totalTime = Math.floor((Date.now() - gameStartTime) / 1000);
    
    try {
      await fetch('http://localhost:5000/api/trivia/save-score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: username,
          total_score: score,
          questions_answered: questions.length,
          correct_answers: correctAnswers,
          time_taken: totalTime
        })
      });

      // Refresh leaderboard
      await fetchLeaderboard();
      
    } catch (error) {
      console.error('Error saving score:', error);
    }

    setGameState('finished');
  };

  const resetGame = () => {
    setGameState('menu');
    setCurrentQuestion(0);
    setQuestions([]);
    setScore(0);
    setTimeLeft(30);
    setSelectedAnswer('');
    setCorrectAnswers(0);
    setShowAnswer(false);
    setLastAnswerResult(null);
  };

  const getOptionColor = (option) => {
    if (!showAnswer) return 'primary';
    if (option === lastAnswerResult?.correct_answer) return 'primary';
    if (option === selectedAnswer && !lastAnswerResult?.correct) return 'primary';
    return 'primary';
  };

  const getOptionSx = (option) => {
    const baseSx = {
      py: 2,
      textAlign: 'left',
      justifyContent: 'flex-start',
      textTransform: 'none'
    };
    
    if (!showAnswer) return baseSx;
    
    if (option === lastAnswerResult?.correct_answer) {
      return { ...baseSx, bgcolor: 'success.main', color: 'white', '&:hover': { bgcolor: 'success.dark' } };
    }
    
    if (option === selectedAnswer && !lastAnswerResult?.correct) {
      return { ...baseSx, bgcolor: 'error.main', color: 'white', '&:hover': { bgcolor: 'error.dark' } };
    }
    
    return baseSx;
  };

  const getOptionVariant = (option) => {
    if (!showAnswer) return 'outlined';
    if (option === lastAnswerResult?.correct_answer) return 'contained';
    if (option === selectedAnswer) return 'contained';
    return 'outlined';
  };

  // Menu Screen
  if (gameState === 'menu') {
    return (
      <Container maxWidth="md">
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h1" sx={{ fontSize: 60, color: 'primary.main', mb: 2 }}>
            🧠
          </Typography>
          <Typography variant="h2" component="h1" gutterBottom>
            Eco-Trivia Sprint
          </Typography>
          <Typography variant="h6" color="text.secondary" paragraph>
            Test your environmental knowledge and climb the leaderboard!
          </Typography>

          <Paper elevation={3} sx={{ p: 4, mt: 4, maxWidth: 500, mx: 'auto' }}>
            <Typography variant="h5" gutterBottom>
              Enter your username to test your eco-knowledge!
            </Typography>
            
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Your Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              sx={{ mb: 3 }}
            />

            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary">
                Correct answers are +40 points, wrong ones are -10. You have 30 seconds per question.
              </Typography>
            </Box>

            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={startGame}
              disabled={loading}
              sx={{ py: 2, mb: 2 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Start Game'}
            </Button>

            <Button
              variant="outlined"
              size="large"
              fullWidth
              onClick={() => setShowLeaderboard(true)}
            >
              View Leaderboard
            </Button>
          </Paper>

          {/* Game Rules */}
          <Paper elevation={2} sx={{ p: 3, mt: 4, bgcolor: 'primary.light', color: 'white' }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h1" sx={{ fontSize: 40, mb: 1 }}>⏱️</Typography>
                  <Typography variant="h6">30 Seconds</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Per question
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h1" sx={{ fontSize: 40, mb: 1 }}>🎯</Typography>
                  <Typography variant="h6">+40 / -10</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Points system
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h1" sx={{ fontSize: 40, mb: 1 }}>🏆</Typography>
                  <Typography variant="h6">10 Questions</Typography>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Per game
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>
        </Box>

        {/* Leaderboard Dialog */}
        <Dialog 
          open={showLeaderboard} 
          onClose={() => setShowLeaderboard(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <span style={{ fontSize: 24 }}>🏆</span>
              Leaderboard
            </Box>
          </DialogTitle>
          
          <DialogContent>
            <List>
              {leaderboard.map((player, index) => (
                <React.Fragment key={player.username}>
                  <ListItem>
                    <ListItemAvatar>
                      <Avatar sx={{ 
                        bgcolor: index === 0 ? '#ffd700' : index === 1 ? '#c0c0c0' : index === 2 ? '#cd7f32' : '#2e7d32' 
                      }}>
                        {index + 1}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={player.username}
                      secondary={`${player.score} points • ${player.accuracy.toFixed(1)}% accuracy`}
                    />
                    <Chip
                      label={`${player.score} pts`}
                      color={index < 3 ? 'primary' : 'default'}
                      variant={index < 3 ? 'filled' : 'outlined'}
                    />
                  </ListItem>
                  {index < leaderboard.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </DialogContent>
          
          <DialogActions>
            <Button onClick={() => setShowLeaderboard(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Container>
    );
  }

  // Game Screen
  if (gameState === 'playing') {
    const currentQ = questions[currentQuestion];
    const progress = ((currentQuestion + 1) / questions.length) * 100;

    return (
      <Container maxWidth="md">
        <Box sx={{ py: 4 }}>
          {/* Progress Header */}
          <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
            <Grid container alignItems="center" spacing={2}>
              <Grid item xs>
                <Typography variant="body2" color="text.secondary">
                  Question {currentQuestion + 1} of {questions.length}
                </Typography>
                <LinearProgress variant="determinate" value={progress} sx={{ mt: 1 }} />
              </Grid>
              <Grid item>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip label={`Score: ${score}`} color="primary" />
                  <Chip 
                    label={`⏱️ ${timeLeft}s`} 
                    color={timeLeft <= 10 ? 'error' : 'default'}
                    variant={timeLeft <= 10 ? 'filled' : 'outlined'}
                  />
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Question */}
          <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              {currentQ?.question}
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <Grid container spacing={2}>
                {['A', 'B', 'C', 'D'].map((option) => (
                  <Grid item xs={12} sm={6} key={option}>
                    <Button
                      fullWidth
                      variant={getOptionVariant(option)}
                      color={getOptionColor(option)}
                      onClick={() => submitAnswer(option)}
                      disabled={showAnswer}
                      sx={getOptionSx(option)}
                    >
                      <strong>{option}:</strong>&nbsp;{currentQ?.options[option]}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Paper>

          {/* Answer Explanation */}
          {showAnswer && lastAnswerResult && (
            <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
              <Alert 
                severity={lastAnswerResult.correct ? 'success' : 'error'}
                sx={{ mb: 2 }}
              >
                <strong>
                  {lastAnswerResult.correct ? '🎉 Correct!' : '❌ Wrong!'}
                </strong>
                {' '}
                {lastAnswerResult.correct 
                  ? `+${lastAnswerResult.points_earned} points` 
                  : `${lastAnswerResult.points_earned} points`}
              </Alert>
              
              <Typography variant="body1" paragraph>
                <strong>Correct Answer:</strong> {lastAnswerResult.correct_answer}
              </Typography>
              
              {lastAnswerResult.explanation && (
                <Typography variant="body2" color="text.secondary">
                  {lastAnswerResult.explanation}
                </Typography>
              )}

              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Button
                  variant="contained"
                  onClick={nextQuestion}
                  size="large"
                >
                  {currentQuestion + 1 < questions.length ? 'Next Question' : 'Finish Game'}
                </Button>
              </Box>
            </Paper>
          )}
        </Box>
      </Container>
    );
  }

  // Results Screen
  if (gameState === 'finished') {
    const accuracy = questions.length > 0 ? (correctAnswers / questions.length) * 100 : 0;
    
    return (
      <Container maxWidth="md">
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h1" sx={{ fontSize: 80, mb: 2 }}>
            🏆
          </Typography>
          <Typography variant="h3" gutterBottom>
            Game Complete!
          </Typography>
          <Typography variant="h6" color="text.secondary" paragraph>
            Great job, {username}! Here are your results:
          </Typography>

          <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" color="primary.main">{score}</Typography>
                  <Typography variant="h6">Total Score</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" color="success.main">{correctAnswers}</Typography>
                  <Typography variant="h6">Correct Answers</Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h2" color="info.main">{accuracy.toFixed(1)}%</Typography>
                  <Typography variant="h6">Accuracy</Typography>
                </Box>
              </Grid>
            </Grid>

            <Box sx={{ mt: 4 }}>
              <Button
                variant="contained"
                size="large"
                onClick={resetGame}
                sx={{ mr: 2 }}
              >
                Play Again
              </Button>
              <Button
                variant="outlined"
                size="large"
                onClick={() => setShowLeaderboard(true)}
              >
                View Leaderboard
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    );
  }

  return null;
}