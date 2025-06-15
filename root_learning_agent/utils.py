from .sub_agents.checkpoint_generator_agent import Checkpoints
def format_checkpoint_for_display(checkpoints:Checkpoints):
        output:str = ""
        output += ("\n" + "=" * 80)
        output += ("\n")

        output += ("🎯 LEARNING CHECKPOINTS OVERVIEW".center(80))
        output += ("\n")

        output += ("=" * 80 + "\n")
        output += ("\n")

        
        for i, checkpoint in enumerate(checkpoints["checkpoints"], 1):
            # Checkpoint header with number
            output += (f"📍 CHECKPOINT #{i}".center(80))
            output += ("\n")

            output += ("─" * 80 + "\n")
            

            
            # Description section with text wrapping
            output += ("📝 Description:")
            output += ("\n")

            output += ("─" * 40)
            output += ("\n")

            words = checkpoint["description"].split()
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= 70:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    output += (f"  {' '.join(current_line)}")
                    output += ("\n")

                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                output += (f"  {' '.join(current_line)}")
                output += ("\n")
            output += ("\n")
            
            # Success Criteria section
            output += ("✅ Success Criteria:")
            output += ("\n")

            output += ("─" * 40)
            output += ("\n")

            for j, criterion in enumerate(checkpoint["criteria"], 1):
                # Wrap each criterion text
                words = criterion.split()
                current_line = []
                current_length = 0
                first_line = True
                
                for word in words:
                    if current_length + len(word) + 1 <= 66:  # Shorter width to account for numbering
                        current_line.append(word)
                        current_length += len(word) + 1
                    else:
                        if first_line:
                            output += (f"  {j}. {' '.join(current_line)}")
                            output += ("\n")

                            first_line = False
                        else:
                            output += (f"     {' '.join(current_line)}")
                            output += ("\n")

                        current_line = [word]
                        current_length = len(word)
                
                if current_line:
                    if first_line:
                        output += (f"  {j}. {' '.join(current_line)}")
                        output += ("\n")

                    else:
                        output += (f"     {' '.join(current_line)}")
                        output += ("\n")

            output += ("\n")
            
            # Verification Method section
            output +=("🔍 Verification Method:")
            output += ("\n")

            output += ("─" * 40)
            output += ("\n")

            words = checkpoint["verification"].split()
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= 70:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    output += (f"  {' '.join(current_line)}")
                    output += ("\n")

                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                output += (f"  {' '.join(current_line)}")
                output += ("\n")

            output +=("\n")
            
            # Separator between checkpoints
            if i < len(checkpoints["checkpoints"]):
                output += ("~" * 80 + "\n")
                # output += ("\n")

        
        output +=("=" * 80 + "\n")
        output += ("\n")

        return output

def format_verification_results(verifications:dict):
    """Pretty result +=  verification results with improved formatting"""
    result = ""
    result += ("\n" + "=" * 50)
    result += "\n"
    result += ("📊 VERIFICATION RESULTS".center(50))
    result += "\n"
    result += ("=" * 50 + "\n")
    result += "\n"

    # Understanding Level with visual bar
    understanding = verifications['understanding_level']
    bar_length = 20
    filled_length = int(understanding * bar_length)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    
    result += (f"📈 Understanding Level: [{bar}] {understanding * 100:.1f}%\n")
    result += "\n"

    
    # Feedback section
    result += ("💡 Feedback:")
    result += "\n"
    result += (f"{verifications['feedback']}\n")
    result += "\n"
    
    # Suggestions section
    result += ("🎯 Suggestions:")
    result += "\n"
    for i, suggestion in enumerate(verifications['suggestions'], 1):
        result += (f"  {i}. {suggestion}")
    result += "\n"
    
    # Context Alignment
    result += ("🔍 Context Alignment:")
    result += "\n"

    result += (f"{verifications['context_alignment']}\n")
    result += "\n"

    
    result += ("-" * 50 + "\n")

    return result

def format_teaching_results(teachings:dict):
    """Pretty pring  Feynman teaching results with improved formatting"""
    result = ""
    result += ("\n" + "=" * 70)
    result += "\n"
    result += ("🎓 FEYNMAN TEACHING EXPLANATION".center(70))
    result += "\n"
    result += ("=" * 70 + "\n")
    result += "\n"

    # Simplified Explanation section
    result += ("📚 SIMPLIFIED EXPLANATION:")
    result += "\n"
    result += ("─" * 30)
    result += "\n"
    # Split explanation into paragraphs for better readability
    paragraphs = teachings['simplified_explanation'].split('\n')
    for paragraph in paragraphs:
        # Wrap text at 60 characters for better readability
        words = paragraph.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= 60:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            result += (f"{line}")
        result += "\n"
    
    # Key Concepts section
    result += ("💡 KEY CONCEPTS:")
    result += "\n"
    result += ("─" * 30)
    result += "\n"
    for i, concept in enumerate(teachings['key_concepts'], 1):
        result += (f"  {i}. {concept}")
    result += "\n"
    
    # Analogies section
    result += ("🔄 ANALOGIES & EXAMPLES:")
    result += "\n"
    result += ("─" * 30)
    result += "\n"
    for i, analogy in enumerate(teachings['analogies'], 1):
        result += (f"  {i}. {analogy}")
    result += "\n"
    
    result += ("=" * 70 + "\n")

    return result