import OpenAI from 'openai';

// Initialize OpenAI client
// Note: In a production app, you would handle API keys securely on the server side
const openai = new OpenAI({
  apiKey: process.env.NEXT_PUBLIC_OPENAI_API_KEY || 
          "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",
  dangerouslyAllowBrowser: true // For demo purposes only - in production use server-side API calls
});

export const getAIResponse = async (question: string, context: string[]): Promise<string> => {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: "You are a helpful assistant answering a question like a student in class. Phrase it very concisely which represents the thought process of a student answering the question just asked. Sound appropriate. Make it as short as possible that covers key points. Use -> to connect thoughts which should be one or two words"
        },
        {
          role: "user",
          content: `Here's the context to the conversation: ${context.join(', ')}`
        },
        {
          role: "user",
          content: question
        }
      ]
    });

    if (response.choices && response.choices[0].message.content) {
      return response.choices[0].message.content;
    } else {
      throw new Error('No response from OpenAI');
    }
  } catch (error) {
    console.error('Error calling OpenAI:', error);
    throw error;
  }
};
