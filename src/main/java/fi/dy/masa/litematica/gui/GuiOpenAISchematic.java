package fi.dy.masa.litematica.gui;

import fi.dy.masa.litematica.data.DataManager;
import fi.dy.masa.litematica.schematic.ai.HighEffortAIWorkflow;
import fi.dy.masa.litematica.schematic.ai.OpenAIIntegration;
import fi.dy.masa.litematica.schematic.ai.OpenAISchematicBuilder;
import fi.dy.masa.litematica.schematic.ai.OpenAISchematicDSLParser;
import fi.dy.masa.malilib.gui.GuiBase;
import fi.dy.masa.malilib.gui.GuiTextFieldGeneric;
import fi.dy.masa.malilib.gui.Message.MessageType;
import fi.dy.masa.malilib.gui.button.ButtonBase;
import fi.dy.masa.malilib.gui.button.ButtonGeneric;
import fi.dy.masa.malilib.gui.button.IButtonActionListener;
import fi.dy.masa.malilib.util.KeyCodes;
import net.minecraft.client.gui.DrawContext;

public class GuiOpenAISchematic extends GuiBase {

    private GuiTextFieldGeneric promptField;
    private GuiTextFieldGeneric nameField;
    private boolean useHighEffort = false;
    private boolean isGenerating = false;
    private String statusText = "";
    private final java.util.List<String> eventLog = new java.util.ArrayList<>();
    
    private ButtonGeneric generateButton;
    private ButtonGeneric abortButton;
    private ButtonGeneric pauseResumeButton;
    private ButtonGeneric highEffortToggle;

    public GuiOpenAISchematic() {
        this.title = "Generate AI Schematic";
    }

    @Override
    public void initGui() {
        super.initGui();
        
        int x = this.width / 2 - 150;
        int y = 50;
        
        this.promptField = new GuiTextFieldGeneric(x, y, 300, 20, this.textRenderer);
        this.promptField.setMaxLength(512);
        
        this.nameField = new GuiTextFieldGeneric(x, y + 40, 300, 20, this.textRenderer);
        this.nameField.setMaxLength(128);
        this.nameField.setText("ai-test.litematic");
        
        this.promptField.setFocused(true);

        this.highEffortToggle = new ButtonGeneric(x - 120, y + 80, 100, 20, "[ ] High Effort");
        this.addButton(this.highEffortToggle, new IButtonActionListener() {
            @Override
            public void actionPerformedWithButton(ButtonBase button, int mouseButton) {
                if (isGenerating) return;
                useHighEffort = !useHighEffort;
                highEffortToggle.setDisplayString(useHighEffort ? "[X] High Effort" : "[ ] High Effort");
            }
        });

        this.generateButton = new ButtonGeneric(x, y + 80, 100, 20, "Generate");
        this.addButton(this.generateButton, new IButtonActionListener() {
            @Override
            public void actionPerformedWithButton(ButtonBase button, int mouseButton) {
                if (isGenerating) return;
                
                String promptText = promptField.getText();
                String schemName = nameField.getText();

                if (promptText.isEmpty() || schemName.isEmpty()) {
                    addMessage(MessageType.ERROR, "Both fields are required!");
                    return;
                }

                isGenerating = true;
                statusText = "Generating... Please Wait.";
                eventLog.clear();
                eventLog.add("Generation Started...");
                updateButtons();
                
                if (useHighEffort) {
                    HighEffortAIWorkflow.INSTANCE.start(promptText, schemName, new HighEffortAIWorkflow.IProgressCallback() {
                        @Override
                        public void onProgress(String msg) {
                            net.minecraft.client.MinecraftClient.getInstance().execute(() -> {
                                statusText = msg;
                                eventLog.add(msg);
                                if (eventLog.size() > 15) eventLog.remove(0);
                                updateButtons();
                            });
                        }

                        @Override
                        public void onComplete(boolean success, String message) {
                            net.minecraft.client.MinecraftClient.getInstance().execute(() -> {
                                isGenerating = false;
                                statusText = "";
                                eventLog.add(success ? "SUCCESS: " + message : "ERROR: " + message);
                                if (eventLog.size() > 15) eventLog.remove(0);
                                updateButtons();
                                if (success) {
                                    addMessage(MessageType.SUCCESS, message);
                                } else {
                                    addMessage(MessageType.ERROR, message);
                                }
                            });
                        }
                    });
                } else {
                    OpenAIIntegration.generateSchematic(promptText, null).thenAccept(script -> {
                        net.minecraft.client.MinecraftClient.getInstance().execute(() -> {
                            try {
                                System.out.println("AI Script: \n" + script);
                                boolean success = OpenAISchematicBuilder.buildAndSave(schemName, OpenAISchematicDSLParser.parse(script));
                                
                                if (success) {
                                    addMessage(MessageType.SUCCESS, "Schematic built via AI successfully.");
                                    eventLog.add("Schematic built successfully.");
                                } else {
                                    addMessage(MessageType.ERROR, "Failed to compile the DSL script.");
                                    eventLog.add("Failed to compile script.");
                                }
                            } catch (Exception e) {
                                addMessage(MessageType.ERROR, "Crash while compiling script: " + e.getMessage());
                                eventLog.add("Crash: " + e.getMessage());
                            } finally {
                                isGenerating = false;
                                statusText = "";
                                updateButtons();
                            }
                        });
                    }).exceptionally(e -> {
                        net.minecraft.client.MinecraftClient.getInstance().execute(() -> {
                            addMessage(MessageType.ERROR, "API Failure: " + e.getMessage());
                            eventLog.add("API Failure: " + e.getMessage());
                            isGenerating = false;
                            statusText = "";
                            updateButtons();
                        });
                        return null;
                    });
                }
            }
        });
        
        ButtonGeneric cancelButton = new ButtonGeneric(x + 110, y + 80, 80, 20, "Back");
        this.addButton(cancelButton, new IButtonActionListener() {
            @Override
            public void actionPerformedWithButton(ButtonBase button, int mouseButton) {
                if (!isGenerating) {
                    GuiBase.openGui(new GuiMainMenu());
                }
            }
        });

        this.pauseResumeButton = new ButtonGeneric(x + 200, y + 80, 80, 20, "Pause");
        this.pauseResumeButton.setEnabled(false);
        this.addButton(this.pauseResumeButton, new IButtonActionListener() {
            @Override
            public void actionPerformedWithButton(ButtonBase button, int mouseButton) {
                if (useHighEffort && isGenerating) {
                    if (HighEffortAIWorkflow.INSTANCE.getState() == HighEffortAIWorkflow.State.PAUSED) {
                        HighEffortAIWorkflow.INSTANCE.resume();
                        pauseResumeButton.setDisplayString("Pause");
                    } else {
                        HighEffortAIWorkflow.INSTANCE.pause();
                        pauseResumeButton.setDisplayString("Resume");
                    }
                }
            }
        });

        this.abortButton = new ButtonGeneric(x + 290, y + 80, 80, 20, "Abort");
        this.abortButton.setEnabled(false);
        this.addButton(this.abortButton, new IButtonActionListener() {
            @Override
            public void actionPerformedWithButton(ButtonBase button, int mouseButton) {
                if (isGenerating && useHighEffort) {
                    HighEffortAIWorkflow.INSTANCE.abort();
                }
            }
        });
    }

    private void updateButtons() {
        this.generateButton.setEnabled(!isGenerating);
        this.highEffortToggle.setEnabled(!isGenerating);
        this.pauseResumeButton.setEnabled(isGenerating && useHighEffort);
        this.abortButton.setEnabled(isGenerating && useHighEffort);
        
        if (!isGenerating) {
            this.pauseResumeButton.setDisplayString("Pause");
        }
    }

    @Override
    public boolean onMouseClicked(int mouseX, int mouseY, int mouseButton) {
        if (this.promptField.mouseClicked(mouseX, mouseY, mouseButton)) return true;
        if (this.nameField.mouseClicked(mouseX, mouseY, mouseButton)) return true;
        return super.onMouseClicked(mouseX, mouseY, mouseButton);
    }

    @Override
    public boolean onKeyTyped(int keyCode, int scanCode, int modifiers) {
        if (this.promptField.keyPressed(keyCode, scanCode, modifiers)) return true;
        if (this.nameField.keyPressed(keyCode, scanCode, modifiers)) return true;
        
        if (keyCode == KeyCodes.KEY_TAB) {
            if (this.promptField.isFocused()) {
                this.promptField.setFocused(false);
                this.nameField.setFocused(true);
            } else {
                this.promptField.setFocused(true);
                this.nameField.setFocused(false);
            }
            return true;
        }

        return super.onKeyTyped(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean onCharTyped(char charIn, int modifiers) {
        if (this.promptField.charTyped(charIn, modifiers)) return true;
        if (this.nameField.charTyped(charIn, modifiers)) return true;
        return super.onCharTyped(charIn, modifiers);
    }

    @Override
    public void drawContents(DrawContext drawContext, int mouseX, int mouseY, float partialTicks) {
        super.drawContents(drawContext, mouseX, mouseY, partialTicks);
        
        int x = this.width / 2 - 150;
        int y = 50;

        drawContext.drawText(this.textRenderer, "Prompt (Describe your build):", x, y - 10, 0xFFFFFF, true);
        this.promptField.render(drawContext, mouseX, mouseY, partialTicks);
        
        drawContext.drawText(this.textRenderer, "Output File Name:", x, y + 30, 0xFFFFFF, true);
        this.nameField.render(drawContext, mouseX, mouseY, partialTicks);
        
        if (isGenerating || !eventLog.isEmpty()) {
            int logY = y + 120;
            for (String line : eventLog) {
                drawContext.drawText(this.textRenderer, line, x - 50, logY, 0xFFFF00, true);
                logY += 10;
            }
        }
    }
}
