package litematica.gui;

import malilib.gui.BaseScreen;
import malilib.gui.widget.BaseTextFieldWidget;
import malilib.gui.widget.LabelWidget;
import malilib.gui.widget.button.GenericButton;
import malilib.overlay.message.MessageDispatcher;
import litematica.config.Configs;
import litematica.schematic.OpenAIIntegration;
import litematica.schematic.OpenAISchematicBuilder;
import litematica.schematic.OpenAISchematicDSLParser;
import litematica.schematic.LitematicaSchematic;
import litematica.util.LitematicaDirectories;
import malilib.util.position.BlockPos;
import malilib.util.world.BlockState;

import java.util.Map;
import java.nio.file.Path;

public class OpenAISchematicScreen extends BaseScreen {

    protected LabelWidget nameLabel;
    protected BaseTextFieldWidget nameTextField;
    
    protected LabelWidget promptLabel;
    protected BaseTextFieldWidget promptTextField;
    
    protected LabelWidget contextLabel;
    protected BaseTextFieldWidget contextTextField;

    protected GenericButton generateButton;

    public OpenAISchematicScreen() {
        super();
        this.title = "OpenAI Schematic Generator";
        this.setScreenWidthAndHeight(340, 240);
        this.centerOnScreen();
        
        this.nameLabel = new LabelWidget(20, 20, "Schematic Name:");
        this.nameTextField = new BaseTextFieldWidget(300, 16, "");
        this.nameTextField.setText("");
        
        this.promptLabel = new LabelWidget(20, 20, "Prompt:");
        this.promptTextField = new BaseTextFieldWidget(300, 16, "");
        this.promptTextField.setText("");
        
        this.contextLabel = new LabelWidget(20, 20, "Edit Existing (Schematic Name, empty for new):");
        this.contextTextField = new BaseTextFieldWidget(300, 16, "");
        this.contextTextField.setText("");
        
        this.generateButton = GenericButton.create("Generate", this::onGenerateClicked);
    }

    @Override
    protected void reAddActiveWidgets() {
        super.reAddActiveWidgets();
        this.addWidget(this.nameLabel);
        this.addWidget(this.nameTextField);
        this.addWidget(this.promptLabel);
        this.addWidget(this.promptTextField);
        this.addWidget(this.contextLabel);
        this.addWidget(this.contextTextField);
        this.addWidget(this.generateButton);
    }

    @Override
    protected void updateWidgetPositions() {
        super.updateWidgetPositions();
        int x = this.x + 20;
        int y = this.y + 30;

        this.nameLabel.setPosition(x, y);
        this.nameTextField.setPosition(x, y + 12);
        
        y += 40;
        this.promptLabel.setPosition(x, y);
        this.promptTextField.setPosition(x, y + 12);
        
        y += 40;
        this.contextLabel.setPosition(x, y);
        this.contextTextField.setPosition(x, y + 12);
        
        y += 40;
        this.generateButton.setPosition(x, y);
    }

    protected void onGenerateClicked() {
        String apiKey = Configs.Generic.OPENAI_API_KEY.getStringValue();
        if (apiKey == null || apiKey.trim().isEmpty()) {
            MessageDispatcher.error("OpenAI API Key not configured!");
            return;
        }

        String name = this.nameTextField.getText().trim();
        String prompt = this.promptTextField.getText().trim();
        String contextName = this.contextTextField.getText().trim();

        if (name.isEmpty() || prompt.isEmpty()) {
            MessageDispatcher.error("Name and prompt must not be empty!");
            return;
        }
        
        MessageDispatcher.warning("Generating schematic... check console.");

        new Thread(() -> {
            try {
                String contextStr = "";
                // Context prep logic...

                String script = OpenAIIntegration.generateSchematicScript(prompt, apiKey, contextStr);
                Map<BlockPos, BlockState> blockMap = OpenAISchematicDSLParser.parse(script, LitematicaSchematic.CURRENT_MINECRAFT_DATA_VERSION);
                
                if (blockMap == null || blockMap.isEmpty()) {
                    MessageDispatcher.error("Error: Received empty block map from AI.");
                    return;
                }

                LitematicaSchematic schematic = OpenAISchematicBuilder.buildFromBlockMap(name, blockMap);
                if (schematic != null) {
                    Path dir = LitematicaDirectories.getSchematicsBaseDirectory();
                    Path filePath = dir.resolve(name + ".litematic");
                    if (litematica.schematic.util.SchematicFileUtils.writeToFile(schematic, filePath, true)) {
                        MessageDispatcher.success("Success! Schematic saved.");
                    } else {
                        MessageDispatcher.error("Error: Failed to write schematic.");
                    }
                } else {
                    MessageDispatcher.error("Error: Failed to build schematic.");
                }
            } catch (Exception e) {
                MessageDispatcher.error("Error: " + e.getMessage());
                e.printStackTrace();
            }
        }).start();
    }
}
