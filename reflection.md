# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My design includes seven core objects, such as Owner, Pet, CareTask, Constraints, Scheduler, ScheduledTask, and Plan. The Owner class has add_pet(pet) and set_preference(key, value) methods. A CareTask is a single unit of pet care work, the scheduling logic revolves around it. CareTask has conflicts_with(other_task), fits_in_window(start, end), and mark_done() methods.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, I did make design changes. For instance, I added IDs to CareTask and Pet so the remove_task method and future lookups can target a specific instance. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

I considered time budget, day window, blackout windows, task priority, duration, and fixed vs. flexible timing. Priority mattered most since pet care has real urgency differences.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

It greedily schedules high-priority tasks first rather than optimizing total tasks scheduled. This is reasonable because missing a medication task is worse than missing low-priority tasks, even if greedy packing wastes some minutes.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code for design, coding, and testing. I found that it was helpful to prompt in steps over giving it one big prompt. For example, I iterated the UML throughout the project to handle a check for scheduler conflict detection, which wasn't what I originally started with.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
I didn't accept Claude Code's initial UI and backend integration along with the day rollover method. I asked the agent to verify its own code for each method and write tests.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested recurrence rollover, conflict detection (fixed vs. flexible, same pet), blackout windows, and completion status. These cover the trickiest date/overlap logic where silent bugs would be easy to miss.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Fairly confident because of my 17 passing tests. Next I'd test multiple pets competing for the same tight time budget and back-to-back blackout windows.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm satisfied with how Claude Code implemented algorithmic effiencies for sorting, filtering, and conflict detection.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would add a feature to delete or edit tasks.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
My key takeaway is the importance of building your system before diving into coding with AI. It's also crucial to routinely evaluate the code that is being generated, and you can even ask the agent to review its own code. There's many decisions that need to be made as your coding goes on, which could be made in collaboration with the coding agent, and I will take this into consideration the next time I build software.