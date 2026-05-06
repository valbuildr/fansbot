# BBC Fans Bot To-do

## 1.0.0

- [ ] BBC Fans Live system.
   - Allow moderators and helpers to send updates in formatted messages.
- [ ] Create a database backup system.
   - Weekly backups, store locally and on Discord.
- [ ] Add rules model and management commands.
   - Title and descrption fields
   - Allow for channel-specific rules
- [ ] Honeypot channel.
   - A channel where anyone can send messages, but will be banned if they do so. Designed to catch spam bots.
- [ ] Refactor moderation commands.
   - Use modals, (and their new components) rules model, and Components v2.
   - Ban command seems to delete messages from the banned user, ensure that it doesn't.
- [ ] Add 'Colourdle.'
   - 5 random colors, (blue, brown, green, orange, red, white, yellow, and purple) 8 guesses.
   - Normal mode allows for any guess, hard mode requires the usage of previous hints.
   - Create 'Colourdle Ban' role and disallow those who have the role from playing.
- [ ] Add 'Hexle.'
   - Random hex code, (6 chars) must guess the right one within 6 guesses
   - Normal mode allows for any guess, hard mode requires the usage of previous hints.
   - Show colour in an image and accent colour of container.
   - Create 'Hexle Ban' role and disallow those who have the role from playing.
- [ ] Add 'Gamble Frenzy'
   - 2-4 players
   - Various gambling-related games. (Blackjack, Bingo, Roulette, Slots, Lucky Wheel)
   - Players compete to make the most money in a limited amount of time.
   - In round 1, users start with £500 and are challenged to get to £2,500.
   - At the end of the round, those who haven't met quota are eliminated.
   - If everyone has met quota, the person with the least amount of money is eliminated. (Random choice for ties)
   - Repeat until 1 player lasts. Max 4 rounds. Quota doubles each time. Money rolls over.

## After 1.0.0

- [ ] Update `utils.Pagination` to use Components v2 and allow for `ctx`.
- [ ] Create a custom `help` command using `utils.Pagination`.
- [ ] Write tests to use with `pytest` instead of winging it.